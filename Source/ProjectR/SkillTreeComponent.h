#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/DataTable.h"
#include "SkillTreeComponent.generated.h"

class UTexture2D;
class UFontFace;

/** 스킬 표(CSV) 한 줄. 행 이름이 스킬 ID다. Parent가 비어 있으면 중심 스킬. */
USTRUCT(BlueprintType)
struct FSkillTreeRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	FText DisplayName;

	/** 부모 스킬 ID. 비우면 중심(뿌리) 스킬. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	FName Parent;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill", meta = (ClampMin = "0"))
	int32 Cost = 1;

	/** 노드 안에 넣을 스킬 그림. 비우면 이름 글자를 보여준다. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	TSoftObjectPtr<UTexture2D> Icon;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill")
	FText Description;
};

/** 스킬트리 창의 그림과 배치 수치. */
USTRUCT(BlueprintType)
struct FSkillTreeStyle
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Style")
	TObjectPtr<UTexture2D> Background;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Style")
	TObjectPtr<UTexture2D> NodeLocked;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Style")
	TObjectPtr<UTexture2D> NodeAvailable;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Style")
	TObjectPtr<UTexture2D> NodeUnlocked;

	/** 마우스를 올렸을 때 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Style")
	TObjectPtr<UTexture2D> NodeSelected;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Style")
	TObjectPtr<UTexture2D> LineInactive;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Style")
	TObjectPtr<UTexture2D> LineActive;

	/** 노드에 마우스를 올리면 뜨는 설명창 바탕. 위·아래 조각은 비율 그대로, 가운데만 세로로 늘어난다. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Tooltip")
	TObjectPtr<UTexture2D> Tooltip;

	/** 위·아래 조각이 그림 높이에서 차지하는 비율(0~0.5). 장식·도장이 잘리면 키운다. 글이 짧아도 설명창은 이 두 조각보다 작아지지 않는다. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Tooltip", meta = (ClampMin = "0.0", ClampMax = "0.5"))
	float TooltipSliceMargin = 0.14f;

	/** 글자와 테두리 사이 여백. 위아래는 모서리 장식 아래로 글자가 오도록 넉넉히. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Tooltip")
	FMargin TooltipPadding = FMargin(30.f, 52.f, 30.f, 46.f);

	/** 설명창 글꼴. 비우면 엔진 기본 글꼴. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Tooltip")
	TObjectPtr<UFontFace> TooltipFont;

	/** 이름 / 상태 줄 / 설명 글자 크기 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Tooltip")
	FIntVector TooltipFontSizes = FIntVector(22, 15, 17);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Tooltip", meta = (ClampMin = "100.0"))
	float TooltipWidth = 300.f;

	/** 한 단계(부모→자식)마다 중심에서 멀어지는 거리 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout", meta = (ClampMin = "10.0"))
	float RingSpacing = 170.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout", meta = (ClampMin = "10.0"))
	float NodeSize = 84.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout", meta = (ClampMin = "1.0"))
	float LineThickness = 8.f;

	/** 첫 가지가 뻗는 방향(도). -90 = 위쪽 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float StartAngle = -90.f;

	/** 창을 열 때 확대 배율. 1 = 원래 크기 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "View", meta = (ClampMin = "0.1"))
	float InitialZoom = 0.5f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "View", meta = (ClampMin = "0.1"))
	float MinZoom = 0.3f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "View", meta = (ClampMin = "0.1"))
	float MaxZoom = 1.6f;

	/** 휠 한 칸에 바뀌는 배율 (1.15 = 15%) */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "View", meta = (ClampMin = "1.01"))
	float ZoomStep = 1.15f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	FLinearColor TextColor = FLinearColor(0.23f, 0.14f, 0.07f);
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnSkillTreeChanged);

/** 스킬 포인트와 해금한 스킬을 들고 있다. 부모를 해금해야 자식을 찍을 수 있다. */
UCLASS(ClassGroup = (ProjectR), meta = (BlueprintSpawnableComponent))
class PROJECTR_API USkillTreeComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Skill Tree")
	TObjectPtr<UDataTable> SkillTable;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Skill Tree", meta = (ClampMin = "0"))
	int32 SkillPoints = 5;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Skill Tree")
	FSkillTreeStyle Style;

	UPROPERTY(BlueprintAssignable, Category = "Skill Tree")
	FOnSkillTreeChanged OnChanged;

	UFUNCTION(BlueprintPure, Category = "Skill Tree")
	bool IsUnlocked(FName SkillId) const { return UnlockedSkills.Contains(SkillId); }

	UFUNCTION(BlueprintPure, Category = "Skill Tree")
	bool CanUnlock(FName SkillId) const;

	UFUNCTION(BlueprintCallable, Category = "Skill Tree")
	bool TryUnlock(FName SkillId);

	const FSkillTreeRow* FindSkill(FName SkillId) const;

private:
	UPROPERTY(VisibleInstanceOnly, Category = "Skill Tree")
	TSet<FName> UnlockedSkills;
};
