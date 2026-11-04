#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ProjectRCharacter.generated.h"

class UCameraComponent;
class UStaticMeshComponent;
class UInputAction;
class UInputMappingContext;
class UAnimMontage;
struct FInputActionValue;

/**
 * 1인칭 검사 플레이어. 이동·시점·점프 입력과 몽타주 기반 3타 콤보 공격을 처리한다.
 * 몽타주, 검 메시, 소켓 같은 에셋 연결은 블루프린트 자식(BP_PlayerCharacter)에서 한다.
 */
UCLASS()
class PROJECTR_API AProjectRCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AProjectRCharacter();

	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> FirstPersonCamera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> SwordMesh;

	/** 검을 붙일 스켈레톤 본/소켓 이름. */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	FName WeaponSocketName = TEXT("mixamorig_RightHand");

	/** 1인칭 카메라에 걸리지 않도록 숨길 본(하위 본 포함). None이면 숨기지 않는다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera")
	FName HiddenHeadBoneName = TEXT("mixamorig_Head");

	/** 콤보 순서대로 재생할 공격 몽타주. */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	TArray<TObjectPtr<UAnimMontage>> AttackMontages;

	/** 몽타주 길이 대비 타격 판정 시점(0~1). */
	UPROPERTY(EditDefaultsOnly, Category = "Combat", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float HitTimeFraction = 0.4f;

	/** 몽타주 길이 대비 다음 타로 넘어가는 시점(0~1). 이 전에 들어온 공격 입력이 다음 타가 된다. */
	UPROPERTY(EditDefaultsOnly, Category = "Combat", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float ComboTimeFraction = 0.65f;

	/** 타격 판정 거리(cm), 카메라 앞쪽. */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	float AttackRange = 160.f;

	/** 타격 판정 구 반지름(cm). */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	float AttackRadius = 40.f;

	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	float AttackDamage = 10.f;

private:
	void CreateInput();

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);
	void Attack();

	void PlayComboAttack(int32 Index);
	void PerformHitTrace();
	void OnComboTime();
	void OnAttackMontageEnded(UAnimMontage* Montage, bool bInterrupted);
	void ResetCombo();

	UPROPERTY(Transient)
	TObjectPtr<UInputMappingContext> DefaultMappingContext;

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> MoveAction;

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> LookAction;

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> JumpAction;

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> AttackAction;

	/** 현재 재생 중인 콤보 인덱스. 공격 중이 아니면 INDEX_NONE. */
	int32 ComboIndex = INDEX_NONE;
	bool bComboQueued = false;

	FTimerHandle HitTimer;
	FTimerHandle ComboTimer;
};
