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
class UDataTable;
class UStaticMesh;
class AWeaponPickup;
struct FInputActionValue;
struct FWeaponRow;

/**
 * 1인칭 검사 플레이어. 이동·시점·점프 입력, 몽타주 콤보 공격, 스킬 입력을 처리한다.
 * 카메라·메시는 캡슐에 붙어 있어 BP에서 정한 위치·회전(cm, 도)이 그대로 쓰인다. 코드는 덮어쓰지 않는다.
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

	/** 무기 표(DT_Weapons) 행으로 무기를 바꾼다: 손 메시, 공격 몽타주, 근접/탄, 고유 스킬(F). */
	void EquipWeapon(FName WeaponId);
	FName GetCurrentWeapon() const { return CurrentWeapon; }

	/** 바닥 무기 근처에 들어가고 나올 때 무기가 알려 준다. 근처에 있으면 E가 스킬 대신 줍기가 된다. */
	void SetNearbyPickup(AWeaponPickup* Pickup);
	void ClearNearbyPickup(AWeaponPickup* Pickup);

protected:
	virtual void BeginPlay() override;
	virtual float TakeDamage(float DamageAmount, const FDamageEvent& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;

	/** 눈 카메라. 캡슐에 붙고 마우스로 좌우·위아래를 본다. 위치는 BP 뷰포트에서 눈 높이로 맞춘다. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UCameraComponent> FirstPersonCamera;

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

	/** 무기 표. 원본 SourceArt/Data/Weapons.csv */
	UPROPERTY(EditDefaultsOnly, Category = "Weapon")
	TSoftObjectPtr<UDataTable> WeaponTable = TSoftObjectPtr<UDataTable>(FSoftObjectPath(TEXT("/Game/Data/DT_Weapons.DT_Weapons")));

	/** 런을 처음 시작할 때 드는 무기(무기 표 행 이름). 방을 옮기면 들고 있던 무기를 이어서 든다. */
	UPROPERTY(EditDefaultsOnly, Category = "Weapon")
	FName DefaultWeapon = TEXT("Sword");

	/** 검을 붙일 스켈레톤 본/소켓 이름. */
	UPROPERTY(EditDefaultsOnly, Category = "Combat")
	FName WeaponSocketName = TEXT("RightHand");

	/** 카메라 시점 기준으로 항상 더하는 위치 오프셋(cm). X = 앞, Y = 오른쪽, Z = 위. 카메라 위치 자체는 BP 뷰포트에서 옮겨도 된다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera")
	FVector CameraViewOffset = FVector::ZeroVector;

	/** 공격할 때 카메라가 시선 방향으로 나갔다 돌아오는 최대 거리(cm). 0이면 끈다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Attack Push", meta = (ClampMin = "0.0"))
	float AttackCameraPushDistance = 15.f;

	/** 공격 시작부터 카메라가 나갔다가 완전히 돌아올 때까지 걸리는 시간(초). 절반 지점에서 가장 멀리 나간다. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera|Attack Push", meta = (ClampMin = "0.05"))
	float AttackCameraPushTime = 0.4f;

	/** 카메라 앞을 가리지 않게 숨길 본(하위 본 포함). */
	UPROPERTY(EditDefaultsOnly, Category = "Camera")
	TArray<FName> BodyHiddenBoneNames = { TEXT("Neck") };

	/** 숨길 메시 재질 슬롯(머리카락·눈처럼 시야를 가리는 것). */
	UPROPERTY(EditDefaultsOnly, Category = "Camera")
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
	/** 시야를 가리는 본·재질을 숨긴다. */
	void ApplyFirstPersonVisibility();
	void UpdateAttackCameraPush(float DeltaSeconds);

	void CreateInput();

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);
	void Attack();

	/** K: 스킬트리 창을 열고 닫는다. 열려 있는 동안 이동·시점·공격을 막고 커서를 보인다. */
	void ToggleSkillTree();

	/** 0~2 = 젬 칸(Q·E·R), 3 = 무기 칸(F) */
	void UseSkillSlot(int32 Slot);

	const FWeaponRow* FindWeaponRow(FName WeaponId) const;
	void FireWeaponProjectile(const FWeaponRow& Row);
	void PickUpNearbyWeapon();

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

	/** 든 무기의 기본 상대 회전. 공격별 검 회전은 이 위에 더한다. */
	FQuat SwordBaseRotation = FQuat::Identity;

	/** BP에서 맞춘 SwordMesh 상대 Transform·메시. 무기별 오프셋은 이 위에 더한다. */
	FTransform WeaponBaseTransform = FTransform::Identity;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> DefaultWeaponMesh;

	FName CurrentWeapon;

	/** 지금 무기의 콤보 몽타주. 무기 표에 없으면 BP의 AttackMontages */
	UPROPERTY(Transient)
	TArray<TObjectPtr<UAnimMontage>> ActiveAttackMontages;

	/** BP 검 콤보를 쓸 때만 공격별 검 회전을 건다. */
	bool bUseSwordComboRotations = true;

	TWeakObjectPtr<AWeaponPickup> NearbyPickup;

	/** 공격 카메라 전진이 시작된 뒤 지난 시간(초). AttackCameraPushTime 이상이면 쉬는 중. */
	float AttackPushElapsed = TNumericLimits<float>::Max();

	/** 현재 재생 중인 콤보 인덱스. 공격 중이 아니면 INDEX_NONE. */
	int32 ComboIndex = INDEX_NONE;
	bool bComboQueued = false;

	FTimerHandle HitTimer;
	FTimerHandle ComboTimer;
};
