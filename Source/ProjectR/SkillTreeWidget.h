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

	// 빈 곳을 왼쪽 드래그 또는 어디서나 오른쪽 드래그로 이동, 휠로 커서 기준 확대·축소
	virtual FReply NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual FReply NativeOnMouseButtonUp(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual FReply NativeOnMouseMove(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual FReply NativeOnMouseWheel(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;

private:
	void ApplyView();
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

	/** 노드와 선이 올라가는 판. 이 판을 옮기고 확대한다. */
	UPROPERTY(Transient)
	TObjectPtr<UCanvasPanel> Board;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> PointsText;

	FVector2D Pan = FVector2D::ZeroVector;
	float Zoom = 1.f;
	bool bDragging = false;
	FVector2D LastMouse = FVector2D::ZeroVector;

	UPROPERTY(Transient)
	TMap<FName, TObjectPtr<USkillNodeButton>> Nodes;

	/** 선 그림과, 그 선이 이어 주는 자식 스킬 ID(같은 순서) */
	UPROPERTY(Transient)
	TArray<TObjectPtr<UImage>> LineImages;

	TArray<FName> LineChildIds;
	TMap<FName, TArray<FName>> Children;
	TMap<FName, FVector2D> Positions;
};
