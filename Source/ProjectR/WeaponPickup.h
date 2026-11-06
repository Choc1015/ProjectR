#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WeaponPickup.generated.h"

class UDataTable;
class USphereComponent;
class UStaticMeshComponent;
struct FWeaponRow;

/**
 * 바닥에 놓인 무기. 가까이 가서 E를 누르면 들고 있던 무기와 바꾼다(내려놓은 무기가 이 자리에 남는다).
 * 방에 놓고 WeaponId만 고르면 메시는 무기 표에서 가져온다.
 */
UCLASS()
class PROJECTR_API AWeaponPickup : public AActor
{
	GENERATED_BODY()

public:
	AWeaponPickup();

	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void Tick(float DeltaSeconds) override;

	/** 무기 표(DT_Weapons) 행 이름 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	FName WeaponId = TEXT("Staff");

	UPROPERTY(EditAnywhere, Category = "Weapon")
	TSoftObjectPtr<UDataTable> WeaponTable;

	/** 제자리에서 도는 속도(도/초)와 떠 있는 높이·흔들림(cm) */
	UPROPERTY(EditAnywhere, Category = "Look")
	float SpinSpeed = 60.f;

	UPROPERTY(EditAnywhere, Category = "Look")
	float HoverHeight = 60.f;

	UPROPERTY(EditAnywhere, Category = "Look")
	float BobAmount = 8.f;

	/** 이 자리 무기를 NewWeaponId로 바꾼다(줍고 나서 내려놓은 무기). None이면 사라진다. */
	void SetWeapon(FName NewWeaponId);

	const FWeaponRow* FindRow() const;

protected:
	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<USphereComponent> Trigger;

	UPROPERTY(VisibleAnywhere, Category = "Components")
	TObjectPtr<UStaticMeshComponent> Display;

private:
	void RefreshDisplay();

	UFUNCTION()
	void HandleBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
		int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void HandleEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

	float Time = 0.f;
};
