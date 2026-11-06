#include "PlayerSkillComponent.h"

#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Camera/CameraComponent.h"
#include "Engine/OverlapResult.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "PlayerStatsComponent.h"
#include "NiagaraSystem.h"
#include "ProjectRProjectile.h"
#include "TimerManager.h"

UPlayerSkillComponent::UPlayerSkillComponent()
{
	WeaponSkill = TEXT("Sword_Dash");
	GemSkills = { TEXT("Gem_Spin"), TEXT("Gem_Slam"), TEXT("Gem_Breath") };
}

void UPlayerSkillComponent::BeginPlay()
{
	Super::BeginPlay();
	Stats = GetOwner()->FindComponentByClass<UPlayerStatsComponent>();
}

const FSkillRow* UPlayerSkillComponent::FindSkill(FName SkillId) const
{
	return SkillTable && !SkillId.IsNone() ? SkillTable->FindRow<FSkillRow>(SkillId, TEXT("Skills"), false) : nullptr;
}

FName UPlayerSkillComponent::GetSlotSkill(int32 Slot) const
{
	if (Slot == WeaponSlot)
	{
		return WeaponSkill;
	}
	return GemSkills.IsValidIndex(Slot) ? GemSkills[Slot] : NAME_None;
}

float UPlayerSkillComponent::GetRemainingCooldown(FName SkillId) const
{
	const double* Ready = ReadyTime.Find(SkillId);
	return Ready ? FMath::Max(0.f, float(*Ready - GetWorld()->GetTimeSeconds())) : 0.f;
}

bool UPlayerSkillComponent::IsBusy() const
{
	return GetWorld()->GetTimeSeconds() < BusyUntil;
}

bool UPlayerSkillComponent::TryUseSlot(int32 Slot)
{
	const FName SkillId = GetSlotSkill(Slot);
	const FSkillRow* Row = FindSkill(SkillId);
	if (!Row || !Stats || IsBusy() || GetRemainingCooldown(SkillId) > 0.f || !Stats->TrySpendMana(Row->ManaCost))
	{
		return false;
	}

	const double Now = GetWorld()->GetTimeSeconds();
	ReadyTime.Add(SkillId, Now + Stats->GetCooldown(Row->Cooldown));

	float Duration = 0.f;
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	UAnimInstance* AnimInstance = Character ? Character->GetMesh()->GetAnimInstance() : nullptr;
	if (UAnimMontage* Montage = Row->Montage.LoadSynchronous(); Montage && AnimInstance)
	{
		Duration = AnimInstance->Montage_Play(Montage, 1.f, EMontagePlayReturnType::Duration);
	}
	// 모션이 없으면 효과가 들어간 뒤 조금 더 묶어 둔다.
	BusyUntil = Now + FMath::Max(Duration, Row->HitDelay + 0.2f);


	GetWorld()->GetTimerManager().SetTimer(EffectTimer, FTimerDelegate::CreateWeakLambda(this, [this, SkillId]()
	{
		ApplyEffect(SkillId);
	}), FMath::Max(0.01f, Row->HitDelay), false);
	return true;
}

void UPlayerSkillComponent::ApplyEffect(FName SkillId)
{
	const FSkillRow* Row = FindSkill(SkillId);
	if (!Row)
	{
		return;
	}

	const FVector Center = GetOwner()->GetActorLocation();
	switch (Row->Effect)
	{
	case ESkillEffect::Dash:
	{
		// 칼을 휘두르는 순간 앞으로 튀어 나가고, 나아갈 길 위의 적을 벤다.
		const FVector Forward = GetAimForward();
		if (ACharacter* Mover = Cast<ACharacter>(GetOwner()))
		{
			const float Gravity = FMath::Max(1.f, -Mover->GetCharacterMovement()->GetGravityZ());
			const float Lift = 150.f;
			const float AirTime = 2.f * Lift / Gravity;
			Mover->LaunchCharacter(Forward * (Row->Range / AirTime) + FVector::UpVector * Lift, true, true);
			// 땅에 닿으면 미끄러지지 않게 멈춘다.
			FTimerHandle StopTimer;
			GetWorld()->GetTimerManager().SetTimer(StopTimer, FTimerDelegate::CreateWeakLambda(Mover, [Mover]()
			{
				FVector& Velocity = Mover->GetCharacterMovement()->Velocity;
				Velocity.X = Velocity.Y = 0.f;
			}), AirTime, false);
		}
		FCollisionQueryParams Params(SCENE_QUERY_STAT(ProjectRSkill), false, GetOwner());
		TArray<FHitResult> Hits;
		GetWorld()->SweepMultiByChannel(Hits, Center, Center + Forward * Row->Range, FQuat::Identity, ECC_Visibility,
			FCollisionShape::MakeSphere(80.f), Params);
		TArray<AActor*> Targets;
		for (const FHitResult& Hit : Hits)
		{
			if (AActor* Actor = Hit.GetActor())
			{
				Targets.AddUnique(Actor);
			}
		}
		DamageActors(Targets, Row->DamageMultiplier);
		break;
	}

	case ESkillEffect::Spin:
		DamageActors(FindActorsAround(Center, Row->Range), Row->DamageMultiplier);
		break;

	case ESkillEffect::Slam:
	{
		const FVector Forward = GetAimForward();
		const float CosHalf = FMath::Cos(FMath::DegreesToRadians(Row->Angle * 0.5f));
		TArray<AActor*> Targets = FindActorsAround(Center, Row->Range);
		Targets.RemoveAll([&](const AActor* Actor)
		{
			const FVector ToTarget = (Actor->GetActorLocation() - Center).GetSafeNormal2D();
			return FVector::DotProduct(ToTarget, Forward) < CosHalf;
		});
		DamageActors(Targets, Row->DamageMultiplier);
		break;
	}

	case ESkillEffect::Heal:
		if (Stats)
		{
			Stats->Heal(Stats->GetStat(EPlayerStat::MaxHealth) * Row->HealPercent / 100.f);
		}
		break;

	case ESkillEffect::Projectile:
	{
		// 눈(카메라) 바로 앞에서 보는 방향(위아래 포함)으로 쏜다.
		const UCameraComponent* Camera = GetOwner()->FindComponentByClass<UCameraComponent>();
		const FVector Eye = Camera ? Camera->GetComponentLocation() : Center;
		const FVector Aim = Camera ? Camera->GetForwardVector() : GetAimForward();
		bool bCrit = false;
		FProjectileLaunch Launch;
		Launch.Location = Eye + Aim * 80.f;
		Launch.Direction = Aim;
		Launch.Mesh = Row->ProjectileMesh.LoadSynchronous();
		Launch.Speed = Row->ProjectileSpeed;
		Launch.Damage = Stats ? Stats->RollOutgoingDamage(true, bCrit) * Row->DamageMultiplier : 0.f;
		Launch.ExplosionRadius = Row->Range;
		Launch.ImpactEffect = Row->ImpactEffect.LoadSynchronous();
		Launch.LightColor = FLinearColor(1.f, 0.4f, 0.1f);
		AProjectRProjectile::Launch(GetOwner(), Launch);
		break;
	}

	default:
		break;
	}
}

TArray<AActor*> UPlayerSkillComponent::FindActorsAround(const FVector& Center, float Radius) const
{
	FCollisionQueryParams Params(SCENE_QUERY_STAT(ProjectRSkill), false, GetOwner());
	TArray<FOverlapResult> Overlaps;
	GetWorld()->OverlapMultiByChannel(Overlaps, Center, FQuat::Identity, ECC_Visibility, FCollisionShape::MakeSphere(Radius), Params);
	TArray<AActor*> Actors;
	for (const FOverlapResult& Overlap : Overlaps)
	{
		if (AActor* Actor = Overlap.GetActor())
		{
			Actors.AddUnique(Actor);
		}
	}
	return Actors;
}

void UPlayerSkillComponent::DamageActors(const TArray<AActor*>& Targets, float Multiplier) const
{
	if (!Stats)
	{
		return;
	}
	const APawn* Pawn = Cast<APawn>(GetOwner());
	for (AActor* Target : Targets)
	{
		// 바닥·벽도 걸리지만 피해를 받아도 아무 일이 없다.
		if (Target && Target->CanBeDamaged() && Target != GetOwner())
		{
			bool bCrit = false;
			const float Damage = Stats->RollOutgoingDamage(true, bCrit) * Multiplier;
			UGameplayStatics::ApplyDamage(Target, Damage, Pawn ? Pawn->GetController() : nullptr, GetOwner(), nullptr);
		}
	}
}

FVector UPlayerSkillComponent::GetAimForward() const
{
	// 1인칭이라 보는 방향(좌우만)이 스킬 방향이다.
	const APawn* Pawn = Cast<APawn>(GetOwner());
	const FRotator Yaw(0.f, Pawn ? Pawn->GetControlRotation().Yaw : GetOwner()->GetActorRotation().Yaw, 0.f);
	return Yaw.Vector();
}
