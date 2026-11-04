#include "SkillTreeComponent.h"

const FSkillTreeRow* USkillTreeComponent::FindSkill(FName SkillId) const
{
	return SkillTable ? SkillTable->FindRow<FSkillTreeRow>(SkillId, TEXT("SkillTree"), false) : nullptr;
}

bool USkillTreeComponent::CanUnlock(FName SkillId) const
{
	const FSkillTreeRow* Row = FindSkill(SkillId);
	if (!Row || IsUnlocked(SkillId) || SkillPoints < Row->Cost)
	{
		return false;
	}
	// 부모가 없거나 표에 없는 ID면 중심 스킬로 본다.
	return Row->Parent.IsNone() || !FindSkill(Row->Parent) || IsUnlocked(Row->Parent);
}

bool USkillTreeComponent::TryUnlock(FName SkillId)
{
	if (!CanUnlock(SkillId))
	{
		return false;
	}
	SkillPoints -= FindSkill(SkillId)->Cost;
	UnlockedSkills.Add(SkillId);
	OnChanged.Broadcast();
	return true;
}
