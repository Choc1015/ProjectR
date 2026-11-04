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

/** 1인칭 카메라와 메시를 붙이는 방식. */
UENUM(BlueprintType)
enum class EFirstPersonCameraMode : uint8
{
	/** 옛 1인칭 템플릿처럼 메시를 카메라에 붙인다. 카메라는 캡슐에 고정되고 팔이 시점을 따라온다. */
	ArmsOnCamera UMETA(DisplayName = "팔을 카메라에 부착"),
	/** 메시는 캡슐에 서 있고 카메라가 매 프레임 본 위치를 따라간다. 모션에 따라 시점이 함께 움직인다. */
	CameraFollowsBody UMETA(DisplayName = "카메라가 몸을 따라감"),
};

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

	virtual void OnConstruction(const FTransform& Transform) override;

	virtual void Tick(float DeltaSeconds) override;

	/** 애님 블루프린트가 걷기·달리기 블렌드를 쓸지. 팔 부착 모드에서 꺼 두면 팔이 대기 자세를 유지한다. */
	bool ShouldUseLocomotionAnimation() const;

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> FirstPersonCamera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> SwordMesh;

	/** 검을 붙일 스켈레톤 본/소켓 이름. */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	FName WeaponSocketName = TEXT("RightHand");

	UPROPERTY(EditAnywhere, Category = "Camera")
	EFirstPersonCameraMode CameraMode = EFirstPersonCameraMode::ArmsOnCamera;

	/** [팔 부착] 숨길 본(하위 본 포함). 팔만 남기도록 목과 다리를 숨긴다. 메시 위치는 CharacterMesh0의 Transform(카메라 기준). */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Arms On Camera")
	TArray<FName> HiddenBoneNames = { TEXT("Neck"), TEXT("LeftUpLeg"), TEXT("RightUpLeg") };

	/** [팔 부착] 숨길 메시 재질 슬롯. 몸통·머리 부분 재질을 숨긴다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Arms On Camera")
	TArray<FName> HiddenMaterialSlotNames = {
		TEXT("M_Player_Hair"), TEXT("M_Player_Eye"), TEXT("M_Player_Leather"),
		TEXT("M_Player_Pants"), TEXT("M_Player_Boots"), TEXT("M_Player_Metal") };

	/** [팔 부착] 켜면 팔도 걷기·달리기 모션을 따른다. 끄면 이동 중에도 대기 자세라 몸이 카메라에 들어오지 않는다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Arms On Camera")
	bool bArmsFollowLocomotion = false;

	/** [몸 따라가기] 캡슐 기준 메시 위치. 메시 원점은 발바닥, 미사모 임포트 결과 정면이 -X라 180도 돌린다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	FTransform BodyMeshTransform = FTransform(FRotator(0.f, 180.f, 0.f), FVector(0.f, 0.f, -90.f));

	/** [몸 따라가기] 카메라가 따라갈 본. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	FName CameraBoneName = TEXT("Head");

	/** [몸 따라가기] 본에서 카메라까지 오프셋(cm). X = 시선 앞, Y = 오른쪽, Z = 위. 시선 좌우 회전만 반영한다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	FVector CameraBoneOffset = FVector(10.f, 0.f, 8.f);

	/** [몸 따라가기] 숨길 본. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	TArray<FName> BodyHiddenBoneNames = { TEXT("Neck") };

	/** [몸 따라가기] 숨길 메시 재질 슬롯. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	TArray<FName> BodyHiddenMaterialSlotNames = { TEXT("M_Player_Hair"), TEXT("M_Player_Eye") };

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
	/** CameraMode에 맞게 메시를 붙이고 숨길 본·재질을 적용한다. */
	void ApplyCameraMode();
	void ApplyFirstPersonVisibility(const TArray<FName>& BoneNames, const TArray<FName>& MaterialSlotNames);

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
