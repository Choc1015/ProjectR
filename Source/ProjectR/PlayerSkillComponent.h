#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/DataTable.h"
#include "PlayerSkillComponent.generated.h"

class UAnimMontage;
class UTexture2D;
class UPlayerStatsComponent;

/** 스킬이 끼워지는 곳. 젬은 갈아 끼우고, 무기 스킬은 무기에 붙어 있다. */
UENUM(BlueprintType)
enum class ESkillSlotType : uint8
{
	Weapon	UMETA(DisplayName = "무기"),
	Gem		UMETA(DisplayName = "젬"),
};

/** 스킬이 하는 일. 새 종류는 여기와 UPlayerSkillComponent::ApplyEffect에 추가한다. */
UENUM(BlueprintType)
enum class ESkillEffect : uint8
{
	Dash	UMETA(DisplayName = "돌진: 앞으로 Range만큼 나가며 경로의 적 타격"),
	Spin	UMETA(DisplayName = "회전: 내 주변 Range 안 모두 타격"),
	Slam	UMETA(DisplayName = "내려찍기: 앞쪽 Range, Angle 부채꼴 타격"),
	Heal	UMETA(DisplayName = "회복: 최대 체력의 HealPercent% 회복"),
};

/** 스킬 표(CSV) 한 줄. 행 이름이 스킬 ID. */
USTRUCT(BlueprintType)
struct FSkillRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	ESkillSlotType Type = ESkillSlotType::Gem;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	ESkillEffect Effect = ESkillEffect::Spin;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill", meta = (ClampMin = "0"))
	float ManaCost = 20.f;

	/** 초 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill", meta = (ClampMin = "0"))
	float Cooldown = 5.f;

	/** 피해 = 스킬 공격력 × 이 값 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill", meta = (ClampMin = "0"))
	float DamageMultiplier = 1.f;

	/** cm. 돌진 거리 / 타격 반지름 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill", meta = (ClampMin = "0"))
	float Range = 300.f;

	/** 부채꼴 전체 각도(도). Slam만 쓴다. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill", meta = (ClampMin = "0", ClampMax = "360"))
	float Angle = 90.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill", meta = (ClampMin = "0"))
	float HealPercent = 0.f;

	/** 시작부터 효과가 들어가기까지(초). 모션에서 칼이 닿는 순간에 맞춘다. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill", meta = (ClampMin = "0"))
	float HitDelay = 0.3f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	TSoftObjectPtr<UAnimMontage> Montage;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	TSoftObjectPtr<UTexture2D> Icon;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	FText Description;
};

/**
 * 스킬 4칸: 젬 3칸(Q·E·R) + 무기 고유 스킬 1칸(F). 마나 소비·재사용 시간은 스탯(지혜 갈래)을 따른다.
 * 무기 액터가 생기면 WeaponSkill은 무기에서 가져온다.
 */
UCLASS(ClassGroup = (ProjectR), meta = (BlueprintSpawnableComponent))
class PROJECTR_API UPlayerSkillComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	static constexpr int32 GemSlotCount = 3;
	/** TryUseSlot에서 무기 스킬 칸 번호 */
	static constexpr int32 WeaponSlot = GemSlotCount;

	UPlayerSkillComponent();

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Skills")
	TObjectPtr<UDataTable> SkillTable;

	/** 지금 무기의 고유 스킬 ID */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skills")
	FName WeaponSkill;

	/** 끼운 젬 스킬 ID (Q, E, R 순서). 비운 칸은 None. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skills")
	TArray<FName> GemSkills;

	/** 0~2 = 젬 칸, 3 = 무기 칸. 마나·재사용 시간이 되면 쓰고 true */
	UFUNCTION(BlueprintCallable, Category = "Skills")
	bool TryUseSlot(int32 Slot);

	UFUNCTION(BlueprintPure, Category = "Skills")
	FName GetSlotSkill(int32 Slot) const;

	/** 남은 재사용 시간(초) */
	UFUNCTION(BlueprintPure, Category = "Skills")
	float GetRemainingCooldown(FName SkillId) const;

	/** 스킬 모션 중이면 기본 공격·다른 스킬을 막는다. */
	UFUNCTION(BlueprintPure, Category = "Skills")
	bool IsBusy() const;

	const FSkillRow* FindSkill(FName SkillId) const;

protected:
	virtual void BeginPlay() override;

private:
	void ApplyEffect(FName SkillId);
	void DamageActors(const TArray<AActor*>& Targets, float Multiplier) const;
	/** 내 위치에서 Radius 안의 액터들(나 제외) */
	TArray<AActor*> FindActorsAround(const FVector& Center, float Radius) const;
	FVector GetAimForward() const;

	UPROPERTY(Transient)
	TObjectPtr<UPlayerStatsComponent> Stats;

	/** 스킬 ID → 다시 쓸 수 있는 시각(월드 시간) */
	TMap<FName, double> ReadyTime;

	/** 이 시각까지 스킬 모션 중 */
	double BusyUntil = 0.0;

	FTimerHandle EffectTimer;
};
