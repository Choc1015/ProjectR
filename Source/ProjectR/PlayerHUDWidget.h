#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "PlayerHUDWidget.generated.h"

class UFontFace;
class USizeBox;
class UTextBlock;
class UTexture2D;
class UPlayerStatsComponent;
struct FCompositeFont;

/** 화면 아래 가운데 HUD(체력·마나 바 + 1~0 아이템 칸)의 그림과 배치 수치 */
USTRUCT(BlueprintType)
struct FPlayerHUDStyle
{
	GENERATED_BODY()

	/** 바 틀. 양끝 장식은 비율 그대로, 가운데만 가로로 늘어난다. 안쪽은 빈 바 색으로 칠해져 있다. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bar")
	TObjectPtr<UTexture2D> BarFrame;

	/** 양끝 장식이 그림 폭에서 차지하는 비율(0~0.5) */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bar", meta = (ClampMin = "0.0", ClampMax = "0.5"))
	float BarCapFraction = 0.075f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bar", meta = (ClampMin = "8.0"))
	float BarHeight = 36.f;

	/** 채워지는 색 막대와 틀 사이 여백(틀 안쪽에 딱 맞게) */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bar")
	FMargin BarFillPadding = FMargin(16.f, 4.f, 16.f, 4.f);

	/** 체력 바와 마나 바 사이 간격 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bar")
	float BarGap = 6.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bar")
	FLinearColor HealthColor = FLinearColor(FColor(142, 42, 34));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Bar")
	FLinearColor ManaColor = FLinearColor(FColor(62, 102, 136));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Slots")
	TObjectPtr<UTexture2D> SlotFrame;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Slots", meta = (ClampMin = "16.0"))
	float SlotSize = 60.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Slots")
	float SlotGap = 6.f;

	/** 바와 아이템 칸을 감싸는 바탕 판. 양끝 장식은 비율 그대로, 가운데만 가로로 늘어난다. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Panel")
	TObjectPtr<UTexture2D> PanelFrame;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Panel", meta = (ClampMin = "0.0", ClampMax = "0.5"))
	float PanelCapFraction = 0.07f;

	/** 판 테두리와 안쪽 바·칸 사이 여백 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Panel")
	FMargin PanelPadding = FMargin(30.f, 18.f, 30.f, 18.f);

	/** 바 줄과 아이템 칸 줄 사이 간격 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float RowGap = 4.f;

	/** 화면 아래 끝에서 띄우는 거리 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float BottomMargin = 24.f;

	/** 비우면 엔진 기본 글꼴 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	TObjectPtr<UFontFace> Font;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	int32 BarFontSize = 18;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	int32 SlotFontSize = 16;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	FLinearColor TextColor = FLinearColor(0.93f, 0.86f, 0.72f);
};

/** 체력·마나 바(왼쪽 반 / 오른쪽 반)와 그 아래 1~0 아이템 칸 10개를 코드로 만든다. 마우스는 통과한다. */
UCLASS()
class PROJECTR_API UPlayerHUDWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void Init(UPlayerStatsComponent* InStats, const FPlayerHUDStyle& InStyle);

	/** 화면 가운데 아래 안내 글(예: "E   스태프 줍기"). 빈 글이면 숨긴다. */
	void SetPrompt(const FText& Text);

protected:
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	UWidget* MakeStretchedFrame(UTexture2D* Texture, float CapFraction, float Height);
	UWidget* MakeBar(float Width, const FLinearColor& Color, TObjectPtr<USizeBox>& OutFill, TObjectPtr<UTextBlock>& OutText);
	UWidget* MakeSlot(int32 Index);
	UTextBlock* MakeText(const FString& Text, int32 Size);
	void UpdateBar(USizeBox* Fill, UTextBlock* Text, float Current, float Max) const;

	UPROPERTY(Transient)
	TObjectPtr<UPlayerStatsComponent> Stats;

	UPROPERTY(Transient)
	FPlayerHUDStyle Style;

	UPROPERTY(Transient)
	TObjectPtr<USizeBox> HealthFill;

	UPROPERTY(Transient)
	TObjectPtr<USizeBox> ManaFill;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> HealthText;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> ManaText;

	/** 색 막대가 가득 찼을 때의 폭 */
	float FillWidth = 0.f;

	TSharedPtr<const FCompositeFont> FontComposite;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> PromptText;

	/** 안내 글은 한글이라 나눔손글씨 펜(HUD 숫자 글꼴 Cinzel엔 한글이 없다) */
	UPROPERTY(Transient)
	TObjectPtr<UObject> PromptFontAsset;

	TSharedPtr<const FCompositeFont> PromptComposite;
};
