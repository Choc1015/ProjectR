#include "InventoryWidget.h"

#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/ScaleBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Engine/FontFace.h"
#include "Engine/Texture2D.h"
#include "Fonts/CompositeFont.h"
#include "PlayerSkillComponent.h"
#include "ProjectRCharacter.h"

namespace
{
	FSlateBrush MakeInvBrush(UTexture2D* Texture, const FVector2D& Size)
	{
		FSlateBrush Brush;
		Brush.DrawAs = ESlateBrushDrawType::Image;
		Brush.SetResourceObject(Texture);
		Brush.ImageSize = Size;
		return Brush;
	}
}

// ---------------------------------------------------------------- 칸

void UInventorySlotWidget::Setup(UInventoryWidget* InOwner, int32 InSlotRef, UTexture2D* Frame, float Size)
{
	Owner = InOwner;
	SlotRef = InSlotRef;
	SlotSize = Size;
	const FInventoryStyle& Style = InOwner->GetStyle();

	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetWidthOverride(Size);
	Box->SetHeightOverride(Size);
	WidgetTree->RootWidget = Box;

	UOverlay* Layers = WidgetTree->ConstructWidget<UOverlay>();
	Box->AddChild(Layers);

	auto AddLayer = [&](UWidget* Widget, const FMargin& LayerPadding)
	{
		UOverlaySlot* OSlot = Layers->AddChildToOverlay(Widget);
		OSlot->SetHorizontalAlignment(HAlign_Fill);
		OSlot->SetVerticalAlignment(VAlign_Fill);
		OSlot->SetPadding(LayerPadding);
	};

	UImage* FrameImage = WidgetTree->ConstructWidget<UImage>();
	FrameImage->SetBrush(MakeInvBrush(Frame, FVector2D(Size)));
	AddLayer(FrameImage, FMargin(0.f));

	Icon = WidgetTree->ConstructWidget<UImage>();
	Icon->SetVisibility(ESlateVisibility::HitTestInvisible);
	AddLayer(Icon, FMargin(Size * Style.IconPadding));

	Hover = WidgetTree->ConstructWidget<UImage>();
	Hover->SetBrush(MakeInvBrush(Style.HoverFrame.LoadSynchronous(), FVector2D(Size)));
	Hover->SetVisibility(ESlateVisibility::Hidden);
	AddLayer(Hover, FMargin(0.f));

	CountText = WidgetTree->ConstructWidget<UTextBlock>();
	CountText->SetFont(InOwner->MakeFont(Style.CountFontSize));
	CountText->SetColorAndOpacity(FSlateColor(Style.InkColor));
	CountText->SetVisibility(ESlateVisibility::HitTestInvisible);
	UOverlaySlot* CountSlot = Layers->AddChildToOverlay(CountText);
	CountSlot->SetHorizontalAlignment(HAlign_Right);
	CountSlot->SetVerticalAlignment(VAlign_Bottom);
	CountSlot->SetPadding(FMargin(0.f, 0.f, Size * 0.1f, Size * 0.04f));

	Refresh();
}

void UInventorySlotWidget::Refresh()
{
	const UInventoryWidget* Widget = Owner.Get();
	const UInventoryComponent* Inventory = Widget ? Widget->GetInventory() : nullptr;
	if (!Inventory || !Icon)
	{
		return;
	}
	const FInventoryStack Stack = Inventory->GetSlot(SlotRef);
	const FItemRow* Row = Inventory->FindItem(Stack.ItemId);
	UTexture2D* Texture = Row && !Stack.IsEmpty() ? Row->Icon.LoadSynchronous() : nullptr;
	Icon->SetBrush(MakeInvBrush(Texture, FVector2D(SlotSize)));
	Icon->SetVisibility(Texture ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Hidden);
	CountText->SetText(Stack.Count > 1 ? FText::AsNumber(Stack.Count) : FText::GetEmpty());
}

FReply UInventorySlotWidget::NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	UInventoryWidget* Widget = Owner.Get();
	if (!Widget)
	{
		return FReply::Unhandled();
	}
	if (InMouseEvent.GetEffectingButton() == EKeys::RightMouseButton)
	{
		Widget->GetInventory()->QuickUse(SlotRef);
		Widget->ShowInfo(SlotRef);
		return FReply::Handled();
	}
	if (InMouseEvent.GetEffectingButton() == EKeys::LeftMouseButton && !Widget->GetInventory()->GetSlot(SlotRef).IsEmpty())
	{
		return UWidgetBlueprintLibrary::DetectDragIfPressed(InMouseEvent, this, EKeys::LeftMouseButton).NativeReply;
	}
	return FReply::Handled();
}

void UInventorySlotWidget::NativeOnDragDetected(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent, UDragDropOperation*& OutOperation)
{
	const UInventoryWidget* Widget = Owner.Get();
	if (!Widget)
	{
		return;
	}
	UInventoryDragOperation* Operation = NewObject<UInventoryDragOperation>(this);
	Operation->FromRef = SlotRef;
	Operation->Pivot = EDragPivot::CenterCenter;

	// 끄는 동안 마우스에 아이콘만 따라다닌다.
	UImage* Visual = WidgetTree->ConstructWidget<UImage>();
	Visual->SetBrush(Icon->GetBrush());
	Visual->SetDesiredSizeOverride(FVector2D(SlotSize * (1.f - 2.f * Widget->GetStyle().IconPadding)));
	Visual->SetVisibility(ESlateVisibility::HitTestInvisible);
	Operation->DefaultDragVisual = Visual;
	OutOperation = Operation;
}

bool UInventorySlotWidget::NativeOnDrop(const FGeometry& InGeometry, const FDragDropEvent& InDragDropEvent, UDragDropOperation* InOperation)
{
	const UInventoryDragOperation* Operation = Cast<UInventoryDragOperation>(InOperation);
	UInventoryWidget* Widget = Owner.Get();
	if (!Operation || !Widget)
	{
		return false;
	}
	Widget->GetInventory()->MoveItem(Operation->FromRef, SlotRef);
	Widget->ShowInfo(SlotRef);
	return true;
}

void UInventorySlotWidget::NativeOnMouseEnter(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	Super::NativeOnMouseEnter(InGeometry, InMouseEvent);
	Hover->SetVisibility(ESlateVisibility::HitTestInvisible);
	if (UInventoryWidget* Widget = Owner.Get())
	{
		Widget->ShowInfo(SlotRef);
	}
}

void UInventorySlotWidget::NativeOnMouseLeave(const FPointerEvent& InMouseEvent)
{
	Super::NativeOnMouseLeave(InMouseEvent);
	Hover->SetVisibility(ESlateVisibility::Hidden);
	if (UInventoryWidget* Widget = Owner.Get())
	{
		Widget->HideInfo(SlotRef);
	}
}

// ---------------------------------------------------------------- 창

void UInventoryWidget::Init(AProjectRCharacter* InCharacter, UInventoryComponent* InInventory)
{
	Character = InCharacter;
	Inventory = InInventory;
	SetIsFocusable(true);
	Build();
	ChangedHandle = Inventory->OnChanged.AddUObject(this, &UInventoryWidget::RefreshAll);
}

void UInventoryWidget::NativeDestruct()
{
	if (Inventory)
	{
		Inventory->OnChanged.Remove(ChangedHandle);
	}
	Super::NativeDestruct();
}

FReply UInventoryWidget::NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent)
{
	const FKey Key = InKeyEvent.GetKey();
	if ((Key == EKeys::Escape || Key == EKeys::I) && Character.IsValid())
	{
		Character->ToggleInventory();
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
}

FSlateFontInfo UInventoryWidget::MakeFont(int32 Size) const
{
	if (Font.IsValid())
	{
		return FSlateFontInfo(Font, Size);
	}
	FSlateFontInfo Info = FCoreStyle::GetDefaultFontStyle("Regular", Size);
	return Info;
}

UTextBlock* UInventoryWidget::AddText(const FText& Text, int32 Size, const FVector2D& Position, float WrapWidth)
{
	UTextBlock* Block = WidgetTree->ConstructWidget<UTextBlock>();
	Block->SetText(Text);
	Block->SetFont(MakeFont(Size));
	Block->SetColorAndOpacity(FSlateColor(GetStyle().InkColor));
	Block->SetJustification(ETextJustify::Center);
	Block->SetVisibility(ESlateVisibility::HitTestInvisible);
	UCanvasPanelSlot* CSlot = Board->AddChildToCanvas(Block);
	CSlot->SetAlignment(FVector2D(0.5, 0.0));
	CSlot->SetPosition(Position);
	if (WrapWidth > 0.f)
	{
		Block->SetAutoWrapText(true);
		CSlot->SetAutoSize(false);
		CSlot->SetSize(FVector2D(WrapWidth, Size * 4.0));
	}
	else
	{
		CSlot->SetAutoSize(true);
	}
	return Block;
}

void UInventoryWidget::AddSlot(int32 SlotRef, UTexture2D* Frame, float Size, const FVector2D& Center)
{
	UInventorySlotWidget* SlotWidget = CreateWidget<UInventorySlotWidget>(this, UInventorySlotWidget::StaticClass());
	SlotWidget->Setup(this, SlotRef, Frame, Size);
	UCanvasPanelSlot* CSlot = Board->AddChildToCanvas(SlotWidget);
	CSlot->SetAlignment(FVector2D(0.5, 0.5));
	CSlot->SetSize(FVector2D(Size));
	CSlot->SetPosition(Center);
	Slots.Add(SlotWidget);
}

void UInventoryWidget::Build()
{
	const FInventoryStyle& Style = GetStyle();

	if (UFontFace* FontFace = Style.Font.LoadSynchronous())
	{
		TSharedRef<FCompositeFont> Composite = MakeShared<FCompositeFont>();
		FTypefaceEntry& Entry = Composite->DefaultTypeface.Fonts.Add_GetRef(FTypefaceEntry(TEXT("Regular")));
		Entry.Font = FFontData(FontFace);
		Font = Composite;
		FontAsset = FontFace;
	}

	// 검은 바탕이 화면을 덮고, 일지 그림은 비율을 지킨 채 화면에 꽉 맞춘다.
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Root;

	UImage* Cover = WidgetTree->ConstructWidget<UImage>();
	Cover->SetColorAndOpacity(Style.CoverColor);
	UCanvasPanelSlot* CoverSlot = Root->AddChildToCanvas(Cover);
	CoverSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	CoverSlot->SetOffsets(FMargin(0.f));

	UScaleBox* Fit = WidgetTree->ConstructWidget<UScaleBox>();
	Fit->SetStretch(EStretch::ScaleToFit);
	UCanvasPanelSlot* FitSlot = Root->AddChildToCanvas(Fit);
	FitSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	FitSlot->SetOffsets(FMargin(0.f));

	USizeBox* BoardBox = WidgetTree->ConstructWidget<USizeBox>();
	BoardBox->SetWidthOverride(Style.BoardSize.X);
	BoardBox->SetHeightOverride(Style.BoardSize.Y);
	Fit->AddChild(BoardBox);

	Board = WidgetTree->ConstructWidget<UCanvasPanel>();
	BoardBox->AddChild(Board);

	UImage* Backdrop = WidgetTree->ConstructWidget<UImage>();
	Backdrop->SetBrush(MakeInvBrush(Style.Backdrop.LoadSynchronous(), Style.BoardSize));
	UCanvasPanelSlot* BackdropSlot = Board->AddChildToCanvas(Backdrop);
	BackdropSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	BackdropSlot->SetOffsets(FMargin(0.f));

	const double LeftX = Style.PageCenterX.X;
	const double RightX = Style.PageCenterX.Y;

	// 왼쪽: 장비(무기 1칸 + 젬 Q·E·R)
	AddText(FText::FromString(TEXT("장비")), Style.TitleFontSize, FVector2D(LeftX, Style.TitleY));
	AddSlot(UInventoryComponent::WeaponSlotRef, Style.WeaponSlotFrame.LoadSynchronous(), Style.WeaponSlotSize, FVector2D(LeftX, Style.WeaponSlotY));

	static const TCHAR* GemKeys[] = { TEXT("Q"), TEXT("E"), TEXT("R") };
	UTexture2D* GemFrame = Style.GemSlotFrame.LoadSynchronous();
	for (int32 i = 0; i < UPlayerSkillComponent::GemSlotCount; ++i)
	{
		const FVector2D Center(LeftX + (i - (UPlayerSkillComponent::GemSlotCount - 1) * 0.5) * Style.GemSlotYSpacing.Y, Style.GemSlotYSpacing.X);
		AddSlot(UInventoryComponent::GemSlotRef(i), GemFrame, Style.GemSlotSize, Center);
		if (i < UE_ARRAY_COUNT(GemKeys))
		{
			AddText(FText::FromString(GemKeys[i]), Style.TextFontSize, Center + FVector2D(0.0, Style.GemSlotSize * 0.5 + 2.0));
		}
	}

	InfoName = AddText(FText::GetEmpty(), Style.TitleFontSize - 6, FVector2D(LeftX, Style.InfoYWidth.X));
	InfoText = AddText(FText::GetEmpty(), Style.TextFontSize, FVector2D(LeftX, Style.InfoYWidth.X + Style.TitleFontSize + 4.0), Style.InfoYWidth.Y);

	// 오른쪽: 가방
	AddText(FText::FromString(TEXT("가방")), Style.TitleFontSize, FVector2D(RightX, Style.TitleY));
	const int32 Columns = FMath::Max(1, Style.BagColumns);
	const double Cell = Style.BagCellGap.X;
	const double Gap = Style.BagCellGap.Y;
	const double GridWidth = Columns * Cell + (Columns - 1) * Gap;
	UTexture2D* SlotFrame = Style.SlotFrame.LoadSynchronous();
	const int32 BagCount = Inventory->GetBag().Num();
	for (int32 i = 0; i < BagCount; ++i)
	{
		const int32 Row = i / Columns;
		const int32 Column = i % Columns;
		const FVector2D Center(RightX - GridWidth * 0.5 + Column * (Cell + Gap) + Cell * 0.5, Style.BagTop + Row * (Cell + Gap) + Cell * 0.5);
		AddSlot(i, SlotFrame, Cell, Center);
	}

	AddText(FText::FromString(TEXT("끌어다 놓기: 장착, 옮기기     우클릭: 사용, 장착     I, Esc: 닫기")), Style.TextFontSize - 2, FVector2D(RightX, Style.HintY));
}

void UInventoryWidget::RefreshAll()
{
	for (UInventorySlotWidget* SlotWidget : Slots)
	{
		if (SlotWidget)
		{
			SlotWidget->Refresh();
		}
	}
	if (InfoSlotRef != TNumericLimits<int32>::Min())
	{
		ShowInfo(InfoSlotRef);
	}
}

void UInventoryWidget::ShowInfo(int32 SlotRef)
{
	InfoSlotRef = SlotRef;
	const FInventoryStack Stack = Inventory->GetSlot(SlotRef);
	const FItemRow* Row = Inventory->FindItem(Stack.ItemId);
	InfoName->SetText(Row && !Stack.IsEmpty() ? Row->DisplayName : FText::GetEmpty());
	InfoText->SetText(Row && !Stack.IsEmpty() ? Row->Description : FText::GetEmpty());
}

void UInventoryWidget::HideInfo(int32 SlotRef)
{
	if (InfoSlotRef == SlotRef)
	{
		InfoSlotRef = TNumericLimits<int32>::Min();
		InfoName->SetText(FText::GetEmpty());
		InfoText->SetText(FText::GetEmpty());
	}
}
