#include "PlayerStatsComponent.h"
#include "SkillTreeComponent.h"

UPlayerStatsComponent::UPlayerStatsComponent()
{
	PrimaryComponentTick.bCanEverTick = true;

	BaseStats = {
		{ EPlayerStat::MaxHealth, 100.f },
		{ EPlayerStat::HealthRegen, 0.f },
		{ EPlayerStat::Armor, 0.f },
		{ EPlayerStat::Poise, 0.f },
		{ EPlayerStat::MaxMana, 100.f },
		{ EPlayerStat::ManaRegen, 5.f },
		{ EPlayerStat::ManaCostReduction, 0.f },
		{ EPlayerStat::CooldownReduction, 0.f },
		{ EPlayerStat::AttackPower, 10.f },
		{ EPlayerStat::SkillPower, 10.f },
		{ EPlayerStat::CritChance, 5.f },
		{ EPlayerStat::CritDamage, 150.f },
		{ EPlayerStat::AttackSpeed, 100.f },
		{ EPlayerStat::ArmorPenetration, 0.f },
		{ EPlayerStat::StaggerDamage, 100.f },
	};
}

void UPlayerStatsComponent::BeginPlay()
{
	Super::BeginPlay();

	SkillTree = GetOwner()->FindComponentByClass<USkillTreeComponent>();
	if (SkillTree)
	{
		SkillTree->OnChanged.AddDynamic(this, &UPlayerStatsComponent::HandleSkillTreeChanged);
	}
	Recalculate();
	Health = GetStat(EPlayerStat::MaxHealth);
	Mana = GetStat(EPlayerStat::MaxMana);
}

float UPlayerStatsComponent::GetStat(EPlayerStat Stat) const
{
	const int32 Index = (int32)Stat;
	if (Index <= 0 || Index >= (int32)EPlayerStat::Count)
	{
		return 0.f;
	}
	const float* Base = BaseStats.Find(Stat);
	return ((Base ? *Base : 0.f) + FlatBonus[Index]) * (1.f + PercentBonus[Index] / 100.f);
}

void UPlayerStatsComponent::Recalculate()
{
	const float OldMaxHealth = GetStat(EPlayerStat::MaxHealth);
	const float OldMaxMana = GetStat(EPlayerStat::MaxMana);

	FMemory::Memzero(FlatBonus);
	FMemory::Memzero(PercentBonus);
	if (SkillTree)
	{
		for (const FName& Id : SkillTree->GetUnlockedSkills())
		{
			const FSkillTreeRow* Row = SkillTree->FindSkill(Id);
			if (Row && Row->Stat != EPlayerStat::None && Row->Stat != EPlayerStat::Count)
			{
				(Row->bStatPercent ? PercentBonus : FlatBonus)[(int32)Row->Stat] += Row->StatValue;
			}
		}
	}

	const float MaxHealth = GetStat(EPlayerStat::MaxHealth);
	const float MaxMana = GetStat(EPlayerStat::MaxMana);
	Health = FMath::Clamp(Health + FMath::Max(0.f, MaxHealth - OldMaxHealth), 0.f, MaxHealth);
	Mana = FMath::Clamp(Mana + FMath::Max(0.f, MaxMana - OldMaxMana), 0.f, MaxMana);
	OnChanged.Broadcast();
}

void UPlayerStatsComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (Health > 0.f)
	{
		Health = FMath::Min(Health + GetStat(EPlayerStat::HealthRegen) * DeltaTime, GetStat(EPlayerStat::MaxHealth));
	}
	Mana = FMath::Min(Mana + GetStat(EPlayerStat::ManaRegen) * DeltaTime, GetStat(EPlayerStat::MaxMana));
}

float UPlayerStatsComponent::ArmorMultiplier(float Armor, float Penetration)
{
	return 100.f / (100.f + FMath::Max(0.f, Armor - Penetration));
}

float UPlayerStatsComponent::RollOutgoingDamage(bool bSkill, bool& bOutCrit) const
{
	const float Damage = GetStat(bSkill ? EPlayerStat::SkillPower : EPlayerStat::AttackPower);
	bOutCrit = FMath::FRand() * 100.f < GetStat(EPlayerStat::CritChance);
	return bOutCrit ? Damage * GetStat(EPlayerStat::CritDamage) / 100.f : Damage;
}

float UPlayerStatsComponent::ApplyIncomingDamage(float Damage, float AttackerPenetration)
{
	const float Taken = FMath::Min(Health, Damage * ArmorMultiplier(GetStat(EPlayerStat::Armor), AttackerPenetration));
	Health -= Taken;
	OnChanged.Broadcast();
	return Taken;
}

bool UPlayerStatsComponent::TrySpendMana(float BaseCost)
{
	const float Cost = BaseCost * FMath::Max(0.f, 1.f - GetStat(EPlayerStat::ManaCostReduction) / 100.f);
	if (Mana < Cost)
	{
		return false;
	}
	Mana -= Cost;
	OnChanged.Broadcast();
	return true;
}

float UPlayerStatsComponent::GetCooldown(float BaseCooldown) const
{
	return BaseCooldown * FMath::Max(0.f, 1.f - GetStat(EPlayerStat::CooldownReduction) / 100.f);
}
