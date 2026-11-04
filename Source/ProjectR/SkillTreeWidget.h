#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "SkillTreeWidget.generated.h"

class UCanvasPanel;
class UImage;
class UTextBlock;
class USkillTreeComponent;
class USkillTreeWidget;

/** 클릭하면 자기 스킬 ID를 위젯에 알려 주는 노드 버튼 */
UCLASS()
class PROJECTR_API USkillNodeButton : public UButton
{
	GENERATED_BODY()

public:
	FName SkillId;
	TWeakObjectPtr<USkillTreeWidget> Owner;

	void BindClick();

private:
	UFUNCTION()
	void HandleClicked();
};

/**
 * 스킬 표를 읽어 중심에서 사방으로 가지를 뻗는 원형 트리를 코드로 만든다.
 * 표에 줄이 추가되면 다음에 창을 열 때 자동으로 다시 배치된다.
 */
UCLASS()
class PROJECTR_API USkillTreeWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void Init(USkillTreeComponent* InSkills);
	void OnNodeClicked(FName SkillId);

protected:
	virtual void NativeDestruct() override;

private:
	void Build();
	void LayoutBranch(FName Id, int32 Depth, float AngleMin, float AngleMax);
	int32 CountLeaves(FName Id) const;
	void AddNode(FName Id, const FVector2D& Position);
	void AddLine(const FVector2D& From, const FVector2D& To, FName ChildId);

	UFUNCTION()
	void Refresh();

	UPROPERTY(Transient)
	TObjectPtr<USkillTreeComponent> Skills;

	UPROPERTY(Transient)
	TObjectPtr<UCanvasPanel> Canvas;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> PointsText;

	UPROPERTY(Transient)
	TMap<FName, TObjectPtr<USkillNodeButton>> Nodes;

	/** 선 그림과, 그 선이 이어 주는 자식 스킬 ID(같은 순서) */
	UPROPERTY(Transient)
	TArray<TObjectPtr<UImage>> LineImages;

	TArray<FName> LineChildIds;
	TMap<FName, TArray<FName>> Children;
	TMap<FName, FVector2D> Positions;
};
