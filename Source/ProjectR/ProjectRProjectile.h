#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ProjectRProjectile.generated.h"

class UNiagaraSystem;
class UPointLightComponent;
class UProjectileMovementComponent;
class USphereComponent;
class UStaticMesh;
class UStaticMeshComponent;

/** 날아가는 탄 하나를 쏠 때 정하는 값 */
struct FProjectileLaunch
{
	FVector Location = FVector::ZeroVector;
	FVector Direction = FVector::ForwardVector;
	UStaticMesh* Mesh = nullptr;
	float Speed = 2500.f;
	float Damage = 10.f;
	/** 0이면 맞은 것 하나만, 크면 맞은 곳 둘레 이 반지름(cm) 안 모두 */
	float ExplosionRadius = 0.f;
	UNiagaraSystem* ImpactEffect = nullptr;
	FLinearColor LightColor = FLinearColor(1.f, 0.6f, 0.2f);
};

/**
 * 스태프 기본 공격 탄과 화염구가 같이 쓰는 투사체. 중력 없이 곧게 날아가 처음 닿은 곳에서 터진다.
 */
UCLASS()
class PROJECTR_API AProjectRProjectile : public AActor
{
	GENERATED_BODY()

public:
	AProjectRProjectile();

	/** Shooter가 쏜 탄을 만든다(쏜 사람은 맞지 않는다). */
	static AProjectRProjectile* Launch(AActor* Shooter, const FProjectileLaunch& Params);

	/** 다른 데 안 닿으면 이 시간(초) 뒤 사라진다. */
	UPROPERTY(EditDefaultsOnly, Category = "Projectile")
	float MaxLifeTime = 3.f;

protected:
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<USphereComponent> Collision;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Visual;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UPointLightComponent> Light;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UProjectileMovementComponent> Movement;

private:
	UFUNCTION()
	void HandleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		FVector NormalImpulse, const FHitResult& Hit);

	float Damage = 0.f;
	float ExplosionRadius = 0.f;

	UPROPERTY(Transient)
	TObjectPtr<UNiagaraSystem> ImpactEffect;

	bool bExploded = false;
};
