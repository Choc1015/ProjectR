#include "PlayerHUDWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Image.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/FontFace.h"
#include "Engine/Texture2D.h"
#include "Fonts/CompositeFont.h"
#include "PlayerStatsComponent.h"

namespace
{
	FSlateBrush MakeHudBrush(UTexture2D* Texture, const FVector2D& Size)
	{
		FSlateBrush Brush;
		Brush.DrawAs = ESlateBrushDrawType::Image;
		Brush.SetResourceObject(Texture);
		Brush.ImageSize = Size;
		return Brush;
	}

	UOverlaySlot* AddFilling(UOverlay* Overlay, UWidget* Child)
	{
		UOverlaySlot* Slot = Overlay->AddChildToOverlay(Child);
		Slot->SetHorizontalAlignment(HAlign_Fill);
		Slot->SetVerticalAlignment(VAlign_Fill);
		return Slot;
	}
}

void UPlayerHUDWidget::Init(UPlayerStatsComponent* InStats, const FPlayerHUDStyle& InStyle)
{
	Stats = InStats;
	Style = InStyle;
	SetVisibility(ESlateVisibility::HitTestInvisible);

	if (Style.Font)
	{
		TSharedRef<FCompositeFont> Composite = MakeShared<FCompositeFont>();
		FTypefaceEntry& Entry = Composite->DefaultTypeface.Fonts.Add_GetRef(FTypefaceEntry(TEXT("Regular")));
		Entry.Font = FFontData(Style.Font);
		FontComposite = Composite;
	}

	UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Canvas"));
	WidgetTree->RootWidget = Canvas;

	// 아이템 칸 줄 폭을 기준으로 체력 바는 왼쪽 반, 마나 바는 오른쪽 반을 채운다.
	const float RowWidth = Style.SlotSize * 10.f + Style.SlotGap * 9.f;
	const float BarWidth = (RowWidth - Style.BarGap) * 0.5f;

	UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>();
	UCanvasPanelSlot* ColumnSlot = Canvas->AddChildToCanvas(Column);
	ColumnSlot->SetAnchors(FAnchors(0.5f, 1.f));
	ColumnSlot->SetAlignment(FVector2D(0.5f, 1.f));
	ColumnSlot->SetPosition(FVector2D(0.f, -Style.BottomMargin));
	ColumnSlot->SetAutoSize(true);

	UHorizontalBox* Bars = WidgetTree->ConstructWidget<UHorizontalBox>();
	Bars->AddChildToHorizontalBox(MakeBar(BarWidth, Style.HealthColor, HealthFill, HealthText));
	UHorizontalBoxSlot* ManaSlot = Bars->AddChildToHorizontalBox(MakeBar(BarWidth, Style.ManaColor, ManaFill, ManaText));
	ManaSlot->SetPadding(FMargin(Style.BarGap, 0.f, 0.f, 0.f));
	Column->AddChildToVerticalBox(Bars)->SetPadding(FMargin(0.f, 0.f, 0.f, Style.RowGap));

	UHorizontalBox* Slots = WidgetTree->ConstructWidget<UHorizontalBox>();
	for (int32 Index = 0; Index < 10; ++Index)
	{
		UHorizontalBoxSlot* SlotSlot = Slots->AddChildToHorizontalBox(MakeSlot(Index));
		SlotSlot->SetPadding(FMargin(Index > 0 ? Style.SlotGap : 0.f, 0.f, 0.f, 0.f));
	}
	Column->AddChildToVerticalBox(Slots);
}

UWidget* UPlayerHUDWidget::MakeBar(float Width, const FLinearColor& Color, TObjectPtr<USizeBox>& OutFill, TObjectPtr<UTextBlock>& OutText)
{
	const float Height = Style.BarHeight;
	FillWidth = FMath::Max(0.f, Width - Style.BarFillPadding.Left - Style.BarFillPadding.Right);

	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetWidthOverride(Width);
	Box->SetHeightOverride(Height);
	UOverlay* Overlay = WidgetTree->ConstructWidget<UOverlay>();
	Box->AddChild(Overlay);

	// 틀: 양끝 장식은 그림 비율 그대로, 가운데만 가로로 늘린다.
	if (UTexture2D* Frame = Style.BarFrame)
	{
		const float Cap = FMath::Clamp(Style.BarCapFraction, 0.01f, 0.49f);
		const float CapWidth = Height * Cap * Frame->GetSurfaceWidth() / FMath::Max(1.f, Frame->GetSurfaceHeight());
		UHorizontalBox* FrameRow = WidgetTree->ConstructWidget<UHorizontalBox>();
		auto AddPart = [&](float U0, float U1, bool bStretch)
		{
			UImage* Part = WidgetTree->ConstructWidget<UImage>();
			FSlateBrush Brush = MakeHudBrush(Frame, FVector2D(bStretch ? 1.f : CapWidth, Height));
			Brush.SetUVRegion(FBox2f(FVector2f(U0, 0.f), FVector2f(U1, 1.f)));
			Part->SetBrush(Brush);
			UHorizontalBoxSlot* PartSlot = FrameRow->AddChildToHorizontalBox(Part);
			PartSlot->SetSize(FSlateChildSize(bStretch ? ESlateSizeRule::Fill : ESlateSizeRule::Automatic));
		};
		AddPart(0.f, Cap, false);
		AddPart(Cap, 1.f - Cap, true);
		AddPart(1.f - Cap, 1.f, false);
		AddFilling(Overlay, FrameRow);
	}

	// 채워지는 색 막대: 왼쪽에서부터 현재/최대 비율만큼 폭이 늘어난다.
	OutFill = WidgetTree->ConstructWidget<USizeBox>();
	OutFill->SetWidthOverride(FillWidth);
	UImage* FillImage = WidgetTree->ConstructWidget<UImage>();
	FillImage->SetColorAndOpacity(Color);
	OutFill->AddChild(FillImage);
	UOverlaySlot* FillSlot = Overlay->AddChildToOverlay(OutFill);
	FillSlot->SetPadding(Style.BarFillPadding);
	FillSlot->SetHorizontalAlignment(HAlign_Left);
	FillSlot->SetVerticalAlignment(VAlign_Fill);

	OutText = MakeText(TEXT(""), Style.BarFontSize);
	UOverlaySlot* TextSlot = Overlay->AddChildToOverlay(OutText);
	TextSlot->SetHorizontalAlignment(HAlign_Center);
	TextSlot->SetVerticalAlignment(VAlign_Center);
	return Box;
}

UWidget* UPlayerHUDWidget::MakeSlot(int32 Index)
{
	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetWidthOverride(Style.SlotSize);
	Box->SetHeightOverride(Style.SlotSize);
	UOverlay* Overlay = WidgetTree->ConstructWidget<UOverlay>();
	Box->AddChild(Overlay);

	UImage* Frame = WidgetTree->ConstructWidget<UImage>();
	if (Style.SlotFrame)
	{
		Frame->SetBrush(MakeHudBrush(Style.SlotFrame, FVector2D(Style.SlotSize)));
	}
	else
	{
		Frame->SetColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.5f));
	}
	AddFilling(Overlay, Frame);

	// 1~9, 마지막 칸은 0 (키보드 숫자 줄 순서)
	UTextBlock* Number = MakeText(FString::FromInt((Index + 1) % 10), Style.SlotFontSize);
	UOverlaySlot* NumberSlot = Overlay->AddChildToOverlay(Number);
	NumberSlot->SetHorizontalAlignment(HAlign_Left);
	NumberSlot->SetVerticalAlignment(VAlign_Top);
	NumberSlot->SetPadding(FMargin(Style.SlotSize * 0.14f, Style.SlotSize * 0.08f, 0.f, 0.f));
	return Box;
}

UTextBlock* UPlayerHUDWidget::MakeText(const FString& Text, int32 Size)
{
	UTextBlock* Block = WidgetTree->ConstructWidget<UTextBlock>();
	Block->SetText(FText::FromString(Text));
	Block->SetColorAndOpacity(FSlateColor(Style.TextColor));
	Block->SetShadowOffset(FVector2D(1.f, 1.f));
	Block->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.8f));
	FSlateFontInfo Font = FontComposite.IsValid() ? FSlateFontInfo(FontComposite, Size) : Block->GetFont();
	Font.Size = Size;
	Block->SetFont(Font);
	return Block;
}

void UPlayerHUDWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	if (Stats)
	{
		UpdateBar(HealthFill, HealthText, Stats->Health, Stats->GetStat(EPlayerStat::MaxHealth));
		UpdateBar(ManaFill, ManaText, Stats->Mana, Stats->GetStat(EPlayerStat::MaxMana));
	}
}

void UPlayerHUDWidget::UpdateBar(USizeBox* Fill, UTextBlock* Text, float Current, float Max) const
{
	if (!Fill || !Text)
	{
		return;
	}
	const float Ratio = Max > 0.f ? FMath::Clamp(Current / Max, 0.f, 1.f) : 0.f;
	Fill->SetWidthOverride(FillWidth * Ratio);
	// 현재 값은 올림(0.4가 남았는데 0으로 보이지 않게), 최대치는 반올림
	Text->SetText(FText::FromString(FString::Printf(TEXT("%d / %d"), FMath::CeilToInt(Current), FMath::RoundToInt(Max))));
}
