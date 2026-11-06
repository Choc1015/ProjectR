#include "ProjectRProjectile.h"

#include "Components/PointLightComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"

AProjectRProjectile::AProjectRProjectile()
{
	PrimaryActorTick.bCanEverTick = false;

	Collision = CreateDefaultSubobject<USphereComponent>(TEXT("Collision"));
	Collision->InitSphereRadius(10.f);
	Collision->SetCollisionProfileName(TEXT("BlockAllDynamic"));
	Collision->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	Collision->SetNotifyRigidBodyCollision(true);
	Collision->OnComponentHit.AddDynamic(this, &AProjectRProjectile::HandleHit);
	SetRootComponent(Collision);

	Visual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Visual"));
	Visual->SetupAttachment(Collision);
	Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Visual->SetCastShadow(false);

	// 탄이 지나가는 길을 비추는 작은 불빛
	Light = CreateDefaultSubobject<UPointLightComponent>(TEXT("Light"));
	Light->SetupAttachment(Collision);
	Light->SetIntensityUnits(ELightUnits::Candelas);
	Light->SetIntensity(40.f);
	Light->SetAttenuationRadius(350.f);
	Light->SetCastShadows(false);

	Movement = CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("Movement"));
	Movement->ProjectileGravityScale = 0.f;
	Movement->bRotationFollowsVelocity = true;
	Movement->bShouldBounce = false;
}

AProjectRProjectile* AProjectRProjectile::Launch(AActor* Shooter, const FProjectileLaunch& Params)
{
	UWorld* World = Shooter ? Shooter->GetWorld() : nullptr;
	if (!World)
	{
		return nullptr;
	}

	FActorSpawnParameters Spawn;
	Spawn.Owner = Shooter;
	Spawn.Instigator = Cast<APawn>(Shooter);
	Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	const FVector Direction = Params.Direction.GetSafeNormal();
	AProjectRProjectile* Projectile = World->SpawnActor<AProjectRProjectile>(StaticClass(), Params.Location, Direction.Rotation(), Spawn);
	if (!Projectile)
	{
		return nullptr;
	}

	Projectile->Collision->IgnoreActorWhenMoving(Shooter, true);
	Projectile->Damage = Params.Damage;
	Projectile->ExplosionRadius = Params.ExplosionRadius;
	Projectile->ImpactEffect = Params.ImpactEffect;
	Projectile->Visual->SetStaticMesh(Params.Mesh);
	Projectile->Light->SetLightColor(Params.LightColor);
	Projectile->Movement->Velocity = Direction * Params.Speed;
	Projectile->SetLifeSpan(Projectile->MaxLifeTime);
	return Projectile;
}

void AProjectRProjectile::HandleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	FVector NormalImpulse, const FHitResult& Hit)
{
	if (bExploded || OtherActor == GetOwner())
	{
		return;
	}
	bExploded = true;

	AController* InstigatorController = GetInstigatorController();
	const FVector Center = Hit.ImpactPoint;
	if (ExplosionRadius > 0.f)
	{
		TArray<AActor*> Ignore = { this, GetOwner() };
		UGameplayStatics::ApplyRadialDamage(this, Damage, Center, ExplosionRadius, nullptr, Ignore, GetOwner(), InstigatorController, true);
	}
	else if (OtherActor)
	{
		UGameplayStatics::ApplyPointDamage(OtherActor, Damage, GetActorForwardVector(), Hit, InstigatorController, GetOwner(), nullptr);
	}

	if (ImpactEffect)
	{
		UNiagaraFunctionLibrary::SpawnSystemAtLocation(this, ImpactEffect, Center, Hit.ImpactNormal.Rotation());
	}
	Destroy();
}
