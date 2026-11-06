#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "RoomMapWidget.generated.h"

class UCanvasPanel;
class URunSubsystem;
class URoomMapWidget;
struct FCompositeFont;

/** 누르면 자기 칸 번호를 지도 위젯에 알려 주는 버튼 */
UCLASS()
class PROJECTR_API URoomMapNodeButton : public UButton
{
	GENERATED_BODY()

public:
	int32 NodeIndex = INDEX_NONE;
	TWeakObjectPtr<URoomMapWidget> Owner;

	void BindClick();

private:
	UFUNCTION()
	void HandleClicked();
};

/**
 * 방 지도 화면. 찢어진 양피지 위에 칸과 점선 길을 코드로 그린다.
 * 갈 수 있는 칸은 숨쉬듯 커졌다 작아지고, 누르면 그 방으로 간다. Esc로 닫는다.
 * 그림·배치 수치는 프로젝트 세팅 > Game > Run Map.
 */
UCLASS()
class PROJECTR_API URoomMapWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void Init(URunSubsystem* InRun);
	void OnNodeClicked(int32 NodeIndex);

protected:
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;
	virtual FReply NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override;

private:
	void Build();
	FVector2D NodePosition(int32 NodeIndex) const;
	void AddDashedLine(const FVector2D& From, const FVector2D& To);

	UPROPERTY(Transient)
	TObjectPtr<URunSubsystem> Run;

	UPROPERTY(Transient)
	TObjectPtr<UCanvasPanel> Board;

	/** 숨쉬는 칸들 */
	UPROPERTY(Transient)
	TArray<TObjectPtr<URoomMapNodeButton>> PulseNodes;

	/** 글꼴 에셋을 붙잡아 둔다(합성 글꼴은 참조만 한다) */
	UPROPERTY(Transient)
	TObjectPtr<UObject> FontAsset;

	TSharedPtr<const FCompositeFont> Font;
	float Time = 0.f;
};
