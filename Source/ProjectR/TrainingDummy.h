#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TrainingDummy.generated.h"

class UStaticMeshComponent;

/**
 * 훈련용 허수아비. 데미지를 받으면 맞은 방향으로 받침을 축으로 흔들리고 맞은 횟수를 센다.
 */
UCLASS()
class PROJECTR_API ATrainingDummy : public AActor
{
	GENERATED_BODY()

public:
	ATrainingDummy();

	virtual void Tick(float DeltaSeconds) override;
	virtual float TakeDamage(float DamageAmount, const FDamageEvent& DamageEvent,
		AController* EventInstigator, AActor* DamageCauser) override;

	UFUNCTION(BlueprintPure, Category = "Dummy")
	int32 GetHitCount() const { return HitCount; }

protected:
	/** 메시 원점이 받침 바닥 중앙이라 이 컴포넌트를 돌리면 받침을 축으로 기운다. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Mesh;

	/** 맞았을 때 최대 기울기(도). */
	UPROPERTY(EditAnywhere, Category = "Dummy")
	float WobbleAngle = 12.f;

	/** 흔들림이 멈출 때까지 걸리는 시간(초). */
	UPROPERTY(EditAnywhere, Category = "Dummy", meta = (ClampMin = "0.05"))
	float WobbleDuration = 0.8f;

	/** 초당 흔들림 횟수. */
	UPROPERTY(EditAnywhere, Category = "Dummy")
	float WobbleFrequency = 3.f;

private:
	int32 HitCount = 0;
	float WobbleElapsed = 0.f;
	/** 액터 로컬 공간에서 기울어지는 수평 방향. */
	FVector WobbleDirection = FVector::ZeroVector;
};
