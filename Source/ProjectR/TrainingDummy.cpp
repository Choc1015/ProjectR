#include "TrainingDummy.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/DamageEvents.h"
#include "Engine/Engine.h"

ATrainingDummy::ATrainingDummy()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = false;

	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(RootComponent);
	Mesh->SetCollisionProfileName(UCollisionProfile::BlockAll_ProfileName);
}

float ATrainingDummy::TakeDamage(float DamageAmount, const FDamageEvent& DamageEvent,
	AController* EventInstigator, AActor* DamageCauser)
{
	const float Applied = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);

	++HitCount;

	FVector HitDirection = DamageCauser ? GetActorLocation() - DamageCauser->GetActorLocation() : -GetActorForwardVector();
	if (DamageEvent.IsOfType(FPointDamageEvent::ClassID))
	{
		HitDirection = static_cast<const FPointDamageEvent&>(DamageEvent).ShotDirection;
	}
	HitDirection.Z = 0.f;
	WobbleDirection = GetActorTransform().InverseTransformVectorNoScale(HitDirection.GetSafeNormal());
	WobbleElapsed = 0.f;
	SetActorTickEnabled(true);

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(static_cast<uint64>(GetUniqueID()), 1.5f, FColor::Yellow,
			FString::Printf(TEXT("%s 명중 %d회 (데미지 %.0f)"), *GetActorNameOrLabel(), HitCount, DamageAmount));
	}

	return Applied;
}

void ATrainingDummy::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	WobbleElapsed += DeltaSeconds;
	const float Alpha = WobbleElapsed / WobbleDuration;
	if (Alpha >= 1.f)
	{
		Mesh->SetRelativeRotation(FRotator::ZeroRotator);
		SetActorTickEnabled(false);
		return;
	}

	// 감쇠 사인파: 처음엔 맞은 방향으로 크게, 점점 작게 되돌아온다.
	const float Angle = WobbleAngle * (1.f - Alpha) * FMath::Sin(Alpha * WobbleDuration * WobbleFrequency * UE_TWO_PI);
	const FVector Axis = FVector::CrossProduct(FVector::UpVector, WobbleDirection).GetSafeNormal();
	Mesh->SetRelativeRotation(FQuat(Axis, FMath::DegreesToRadians(Angle)));
}
