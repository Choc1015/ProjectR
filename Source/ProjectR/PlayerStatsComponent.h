#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PlayerStatsComponent.generated.h"

class USkillTreeComponent;

/** 스킬트리가 올려 주는 플레이어 스탯. % 단위 스탯은 값 자체가 퍼센트다(치명타 확률 5 = 5%). */
UENUM(BlueprintType)
enum class EPlayerStat : uint8
{
	None,
	MaxHealth			UMETA(DisplayName = "최대 체력"),
	HealthRegen			UMETA(DisplayName = "체력 재생(/초)"),
	Armor				UMETA(DisplayName = "방어력"),
	Poise				UMETA(DisplayName = "강인도"),
	MaxMana				UMETA(DisplayName = "최대 마나"),
	ManaRegen			UMETA(DisplayName = "마나 재생(/초)"),
	ManaCostReduction	UMETA(DisplayName = "마나 소비 감소(%)"),
	CooldownReduction	UMETA(DisplayName = "재사용 시간 감소(%)"),
	AttackPower			UMETA(DisplayName = "기본 공격력"),
	SkillPower			UMETA(DisplayName = "스킬 공격력"),
	CritChance			UMETA(DisplayName = "치명타 확률(%)"),
	CritDamage			UMETA(DisplayName = "치명타 피해(%)"),
	AttackSpeed			UMETA(DisplayName = "공격 속도(%)"),
	ArmorPenetration	UMETA(DisplayName = "방어 관통"),
	StaggerDamage		UMETA(DisplayName = "경직 피해(%)"),
	Count				UMETA(Hidden)
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnPlayerStatsChanged);

/**
 * 기본값 + 해금한 스킬의 보너스로 최종 스탯을 계산하고, 현재 체력·마나와 재생을 맡는다.
 * 최종값 = (기본값 + 더하기 보너스) × (1 + 퍼센트 보너스/100)
 */
UCLASS(ClassGroup = (ProjectR), meta = (BlueprintSpawnableComponent))
class PROJECTR_API UPlayerStatsComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UPlayerStatsComponent();

	/** 스킬을 하나도 찍지 않았을 때의 값 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Stats")
	TMap<EPlayerStat, float> BaseStats;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "Stats")
	float Health = 0.f;

	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category = "Stats")
	float Mana = 0.f;

	UPROPERTY(BlueprintAssignable, Category = "Stats")
	FOnPlayerStatsChanged OnChanged;

	UFUNCTION(BlueprintPure, Category = "Stats")
	float GetStat(EPlayerStat Stat) const;

	/** 해금한 스킬로 보너스를 다시 계산한다. 최대치가 오르면 오른 만큼 현재 체력·마나도 채운다. */
	UFUNCTION(BlueprintCallable, Category = "Stats")
	void Recalculate();

	/** 방어력(관통 반영) 비율: 100 / (100 + 방어력) */
	static float ArmorMultiplier(float Armor, float Penetration);

	/** 기본 공격(또는 스킬) 한 번의 피해. 치명타를 굴린다. 상대 방어력은 받는 쪽이 줄인다. */
	float RollOutgoingDamage(bool bSkill, bool& bOutCrit) const;

	/** 받은 피해에 방어력을 적용해 체력을 깎고, 실제로 깎인 양을 돌려준다. */
	float ApplyIncomingDamage(float Damage, float AttackerPenetration = 0.f);

	/** 마나 소비 감소를 적용한 비용을 낼 수 있으면 깎고 true */
	UFUNCTION(BlueprintCallable, Category = "Stats")
	bool TrySpendMana(float BaseCost);

	/** 재사용 시간 감소를 적용한 시간 */
	UFUNCTION(BlueprintPure, Category = "Stats")
	float GetCooldown(float BaseCooldown) const;

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	UFUNCTION()
	void HandleSkillTreeChanged() { Recalculate(); }

	UPROPERTY(Transient)
	TObjectPtr<USkillTreeComponent> SkillTree;

	float FlatBonus[(int32)EPlayerStat::Count] = {};
	float PercentBonus[(int32)EPlayerStat::Count] = {};
};
