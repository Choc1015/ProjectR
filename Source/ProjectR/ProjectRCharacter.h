#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "GameFramework/Character.h"
#include "PlayerHUDWidget.h"
#include "ProjectRCharacter.generated.h"

class UCameraComponent;
class UStaticMeshComponent;
class UInputAction;
class UInputMappingContext;
class UAnimMontage;
class USkillTreeComponent;
class UPlayerStatsComponent;
class UPlayerHUDWidget;
class UPlayerSkillComponent;
class USkillTreeWidget;
struct FInputActionValue;

/** 1인칭 카메라와 메시를 붙이는 방식. */
UENUM(BlueprintType)
enum class EFirstPersonCameraMode : uint8
{
	/** 옛 1인칭 템플릿처럼 메시를 카메라에 붙인다. 카메라는 캡슐에 고정되고 팔이 시점을 따라온다. */
	ArmsOnCamera UMETA(DisplayName = "팔을 카메라에 부착"),
	/** 메시는 캡슐에 서 있고 카메라가 머리 본이 된다. 애니메이션의 머리 위치·회전이 시점에 그대로 실린다. */
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

	/** 애님 블루프린트가 걷기·달리기 블렌드를 쓸지. bPlayLocomotionAnimation을 그대로 돌려준다. */
	bool ShouldUseLocomotionAnimation() const;

protected:
	virtual void BeginPlay() override;
	virtual float TakeDamage(float DamageAmount, const FDamageEvent& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;

	/** 팔 부착 모드 카메라. 캡슐에 붙고 마우스 시점으로 돈다. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> FirstPersonCamera;

	/** 몸 따라가기 모드 카메라. 머리 본에 붙으며, BP에서 옮긴 위치가 그대로 눈 위치가 된다. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> HeadCamera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> SwordMesh;

	/** 스킬 포인트·해금 상태와 스킬트리 창의 그림·배치 수치 */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USkillTreeComponent> SkillTree;

	/** 체력·마나·공격력 등. 기본값 + 해금한 스킬 보너스 */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UPlayerStatsComponent> Stats;

	/** 스킬 4칸: 젬 Q·E·R + 무기 F */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UPlayerSkillComponent> Skills;

	/** 화면 아래 체력·마나 바와 아이템 칸의 그림·배치 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "HUD")
	FPlayerHUDStyle HUDStyle;

	/** 검을 붙일 스켈레톤 본/소켓 이름. */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	FName WeaponSocketName = TEXT("RightHand");

	UPROPERTY(EditAnywhere, Category = "Camera")
	EFirstPersonCameraMode CameraMode = EFirstPersonCameraMode::CameraFollowsBody;

	/** [팔 부착] 숨길 본(하위 본 포함). 팔만 남기도록 목과 다리를 숨긴다. 이 모드에서 CharacterMesh0의 Transform은 카메라 기준이다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Arms On Camera")
	TArray<FName> HiddenBoneNames = { TEXT("Neck"), TEXT("LeftUpLeg"), TEXT("RightUpLeg") };

	/** [팔 부착] 숨길 메시 재질 슬롯. 몸통·머리 부분 재질을 숨긴다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Arms On Camera")
	TArray<FName> HiddenMaterialSlotNames = {
		TEXT("M_Player_Hair"), TEXT("M_Player_Eye"), TEXT("M_Player_Leather"),
		TEXT("M_Player_Pants"), TEXT("M_Player_Boots"), TEXT("M_Player_Metal") };

	/** 켜면 이동할 때 걷기·달리기 모션을 재생한다. 끄면 이동 중에도 대기 자세라 몸을 숙이며 팔이 화면 앞으로 튀어나오지 않는다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera")
	bool bPlayLocomotionAnimation = false;

	/** 카메라 시점 기준으로 항상 더하는 위치 오프셋(cm). X = 앞, Y = 오른쪽, Z = 위. 두 카메라 모드 모두 적용된다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera")
	FVector CameraViewOffset = FVector::ZeroVector;

	/** 공격할 때 카메라가 시선 방향으로 나갔다 돌아오는 최대 거리(cm). 0이면 끈다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Attack Push", meta = (ClampMin = "0.0"))
	float AttackCameraPushDistance = 15.f;

	/** 공격 시작부터 카메라가 나갔다가 완전히 돌아올 때까지 걸리는 시간(초). 절반 지점에서 가장 멀리 나간다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Attack Push", meta = (ClampMin = "0.05"))
	float AttackCameraPushTime = 0.4f;

	/** [몸 따라가기] HeadCamera를 붙일 본/소켓. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	FName CameraBoneName = TEXT("Head");

	/**
	 * [몸 따라가기] 켜면 HeadCamera가 머리 본에 소켓처럼 붙어 위치·회전을 모두 그대로 따른다.
	 * 기준 포즈에서 캐릭터 정면을 보도록 자동으로 맞춘다. 마우스 위아래 시점과 기울기 보정은 쓰지 않는다.
	 * 끄면 위치만 머리를 따르고 회전은 마우스 시점 + 머리 움직임(기울기 없음)이 된다.
	 */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	bool bUseHeadSocketRotation = false;

	/** [몸 따라가기] bUseHeadSocketRotation일 때 자동 정렬 위에 더하는 카메라 회전. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	FRotator HeadSocketRotationOffset = FRotator::ZeroRotator;

	/**
	 * [몸 따라가기] 애니메이션의 머리 움직임을 시점에 얼마나 싣는지. 1 = 머리 그대로, 0 = 마우스 시점만.
	 * 시작 직후 대기 자세의 머리 방향 대비 좌우·위아래 변화량만 더하고, 기울기(롤)는 쓰지 않는다.
	 */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float CameraRotationFollowAlpha = 1.f;

	/** [몸 따라가기] 숨길 본. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	TArray<FName> BodyHiddenBoneNames = { TEXT("Neck") };

	/** [몸 따라가기] 숨길 메시 재질 슬롯. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Camera Follows Body")
	TArray<FName> BodyHiddenMaterialSlotNames = { TEXT("M_Player_Hair"), TEXT("M_Player_Eye") };

	/** 콤보 순서대로 재생할 공격 몽타주. */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	TArray<TObjectPtr<UAnimMontage>> AttackMontages;

	/**
	 * 콤보 타마다 검에 더할 회전(검 로컬 기준, 칼날 축은 Z). 인덱스는 AttackMontages와 같다.
	 * 비어 있거나 모자라면 회전하지 않는다. 공격이 끝나면 원래 각도로 돌아온다.
	 */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	TArray<FRotator> AttackSwordRotationOffsets;

	/**
	 * 몽타주에서 이 이름의 Montage Notify가 오는 순간 타격 판정을 한다.
	 * 몽타주 에디터에서 노티파이를 끌어 칼이 닿는 프레임에 맞춘다. 없으면 HitTimeFraction을 쓴다.
	 */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	FName HitNotifyName = TEXT("Hit");

	/** Hit 노티파이가 없는 몽타주에서 쓰는 타격 판정 시점(몽타주 길이 대비 0~1). */
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


private:
	/** CameraMode에 맞게 메시를 붙이고 숨길 본·재질을 적용한다. */
	void ApplyCameraMode();
	void ApplyFirstPersonVisibility(const TArray<FName>& BoneNames, const TArray<FName>& MaterialSlotNames);

	/** 현재 모드에서 시점으로 쓰는 카메라. */
	UCameraComponent* GetActiveCamera() const;

	/** bUseHeadSocketRotation이면 HeadCamera를 머리 본 회전에 붙이고 정면을 보도록 정렬한다. */
	void AlignHeadCameraToSocket();
	void UpdateHeadCameraRotation(float DeltaSeconds);
	void UpdateAttackCameraPush(float DeltaSeconds);

	void CreateInput();

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);
	void Attack();

	/** K: 스킬트리 창을 열고 닫는다. 열려 있는 동안 이동·시점·공격을 막고 커서를 보인다. */
	void ToggleSkillTree();

	/** 0~2 = 젬 칸(Q·E·R), 3 = 무기 칸(F) */
	void UseSkillSlot(int32 Slot);

	void PlayComboAttack(int32 Index);
	bool HasHitNotify(const UAnimMontage* Montage) const;

	UFUNCTION()
	void OnMontageNotifyBegin(FName NotifyName, const FBranchingPointNotifyPayload& Payload);
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

	UPROPERTY(Transient)
	TObjectPtr<UInputAction> SkillTreeAction;

	/** Q·E·R·F 순서 (젬 3칸, 무기 칸) */
	UPROPERTY(Transient)
	TArray<TObjectPtr<UInputAction>> SkillSlotActions;

	UPROPERTY(Transient)
	TObjectPtr<USkillTreeWidget> SkillTreeWidget;

	UPROPERTY(Transient)
	TObjectPtr<UPlayerHUDWidget> HUDWidget;

	/** [몸 따라가기] 대기 자세에서 머리가 바라보는 방향. 시점에는 이 기준 대비 변화량만 더한다. */
	FRotator CameraBaseline = FRotator::ZeroRotator;
	bool bHasCameraBaseline = false;
	/** 기준을 잡기 전 애니메이션이 대기 자세에 자리 잡도록 기다리는 시간(초). */
	float CameraBaselineDelay = 0.f;

	/** BP에서 정한 검의 기본 상대 회전. 공격별 회전은 이 위에 더한다. */
	FQuat SwordBaseRotation = FQuat::Identity;

	/** 공격 카메라 전진이 시작된 뒤 지난 시간(초). AttackCameraPushTime 이상이면 쉬는 중. */
	float AttackPushElapsed = TNumericLimits<float>::Max();

	/** 현재 재생 중인 콤보 인덱스. 공격 중이 아니면 INDEX_NONE. */
	int32 ComboIndex = INDEX_NONE;
	bool bComboQueued = false;

	FTimerHandle HitTimer;
	FTimerHandle ComboTimer;
};
