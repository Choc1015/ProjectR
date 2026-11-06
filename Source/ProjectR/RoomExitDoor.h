#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RoomExitDoor.generated.h"

class UBoxComponent;

/**
 * 출구 판정. 플레이어가 닿으면 방 지도를 연다.
 * 방 레벨에 직접 놓지 않아도 출구 문 메시(SM_*_ExitDoor) 자리에 자동으로 생긴다(URoomWorldSubsystem).
 * 문 메시의 정면(방 쪽)은 로컬 +Y다.
 */
UCLASS()
class PROJECTR_API ARoomExitDoor : public AActor
{
	GENERATED_BODY()

public:
	ARoomExitDoor();

protected:
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UBoxComponent> Trigger;

private:
	UFUNCTION()
	void HandleOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);
};
