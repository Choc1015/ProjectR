#include "SkillTreeWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/ButtonSlot.h"
#include "Components/SizeBox.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Engine/FontFace.h"
#include "Engine/Texture2D.h"
#include "Fonts/CompositeFont.h"
#include "SkillTreeComponent.h"

namespace
{
	FSlateBrush MakeBrush(UTexture2D* Texture, const FVector2D& Size)
	{
		FSlateBrush Brush;
		Brush.DrawAs = ESlateBrushDrawType::Image;
		Brush.SetResourceObject(Texture);
		Brush.ImageSize = Size;
		Brush.TintColor = FSlateColor(Texture ? FLinearColor::White : FLinearColor::Transparent);
		return Brush;
	}

	UCanvasPanelSlot* PlaceCentered(UCanvasPanel* Canvas, UWidget* Widget, const FVector2D& Position, const FVector2D& Size)
	{
		UCanvasPanelSlot* Slot = Canvas->AddChildToCanvas(Widget);
		Slot->SetAnchors(FAnchors(0.5f, 0.5f));
		Slot->SetAlignment(FVector2D(0.5f, 0.5f));
		Slot->SetPosition(Position);
		Slot->SetSize(Size);
		return Slot;
	}
}

void USkillNodeButton::BindClick()
{
	OnClicked.AddUniqueDynamic(this, &USkillNodeButton::HandleClicked);
}

void USkillNodeButton::HandleClicked()
{
	if (USkillTreeWidget* Widget = Owner.Get())
	{
		Widget->OnNodeClicked(SkillId);
	}
}

void USkillTreeWidget::Init(USkillTreeComponent* InSkills)
{
	Skills = InSkills;
	SetVisibility(ESlateVisibility::Visible); // 빈 곳의 마우스 입력도 받도록
	if (Skills)
	{
		Skills->OnChanged.AddUniqueDynamic(this, &USkillTreeWidget::Refresh);
	}
	Build();
	Refresh();
}

void USkillTreeWidget::NativeDestruct()
{
	if (Skills)
	{
		Skills->OnChanged.RemoveDynamic(this, &USkillTreeWidget::Refresh);
	}
	Super::NativeDestruct();
}

void USkillTreeWidget::OnNodeClicked(FName SkillId)
{
	if (Skills)
	{
		Skills->TryUnlock(SkillId);
	}
}

void USkillTreeWidget::ApplyView()
{
	if (Board)
	{
		if (UCanvasPanelSlot* BoardSlot = Cast<UCanvasPanelSlot>(Board->Slot))
		{
			BoardSlot->SetPosition(Pan);
		}
		Board->SetRenderScale(FVector2D(Zoom));
	}
}

FReply USkillTreeWidget::NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	const FKey Button = InMouseEvent.GetEffectingButton();
	if (Button == EKeys::LeftMouseButton || Button == EKeys::RightMouseButton)
	{
		bDragging = true;
		LastMouse = InGeometry.AbsoluteToLocal(InMouseEvent.GetScreenSpacePosition());
		return FReply::Handled().CaptureMouse(TakeWidget());
	}
	return Super::NativeOnMouseButtonDown(InGeometry, InMouseEvent);
}

FReply USkillTreeWidget::NativeOnMouseButtonUp(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	if (bDragging)
	{
		bDragging = false;
		return FReply::Handled().ReleaseMouseCapture();
	}
	return Super::NativeOnMouseButtonUp(InGeometry, InMouseEvent);
}

FReply USkillTreeWidget::NativeOnMouseMove(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	if (bDragging)
	{
		const FVector2D Mouse = InGeometry.AbsoluteToLocal(InMouseEvent.GetScreenSpacePosition());
		Pan += Mouse - LastMouse;
		LastMouse = Mouse;
		ApplyView();
		return FReply::Handled();
	}
	return Super::NativeOnMouseMove(InGeometry, InMouseEvent);
}

FReply USkillTreeWidget::NativeOnMouseWheel(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	const FSkillTreeStyle Style = Skills ? Skills->Style : FSkillTreeStyle();
	const float NewZoom = FMath::Clamp(Zoom * FMath::Pow(Style.ZoomStep, InMouseEvent.GetWheelDelta()), Style.MinZoom, Style.MaxZoom);

	// 커서 아래 지점이 확대 뒤에도 커서 아래에 남도록 이동량을 맞춘다.
	const FVector2D MouseFromCenter = InGeometry.AbsoluteToLocal(InMouseEvent.GetScreenSpacePosition()) - InGeometry.GetLocalSize() * 0.5f;
	Pan = MouseFromCenter - (MouseFromCenter - Pan) * (NewZoom / Zoom);
	Zoom = NewZoom;
	ApplyView();
	return FReply::Handled();
}

void USkillTreeWidget::Build()
{
	Nodes.Reset();
	TooltipStatus.Reset();
	LineImages.Reset();
	LineChildIds.Reset();
	Children.Reset();
	Positions.Reset();

	Canvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Canvas"));
	WidgetTree->RootWidget = Canvas;

	const FSkillTreeStyle Style = Skills ? Skills->Style : FSkillTreeStyle();

	UImage* Background = WidgetTree->ConstructWidget<UImage>();
	Background->SetBrush(MakeBrush(Style.Background, FVector2D(32.f, 32.f)));
	UCanvasPanelSlot* BackgroundSlot = Canvas->AddChildToCanvas(Background);
	BackgroundSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	BackgroundSlot->SetOffsets(FMargin(0.f));

	// 화면 가운데에 크기 0인 판을 두고 노드를 그 둘레에 놓는다. 판의 위치·배율이 곧 이동·확대다.
	Board = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Board"));
	PlaceCentered(Canvas, Board, FVector2D::ZeroVector, FVector2D::ZeroVector);
	Board->SetRenderTransformPivot(FVector2D(0.5f, 0.5f));
	Board->SetVisibility(ESlateVisibility::SelfHitTestInvisible);

	auto AddText = [this, &Style](const FText& Text, float AnchorY, float OffsetY, int32 FontSize)
	{
		UTextBlock* Block = WidgetTree->ConstructWidget<UTextBlock>();
		Block->SetText(Text);
		Block->SetColorAndOpacity(FSlateColor(Style.TextColor));
		FSlateFontInfo Font = Block->GetFont();
		Font.Size = FontSize;
		Block->SetFont(Font);
		UCanvasPanelSlot* TextSlot = Canvas->AddChildToCanvas(Block);
		TextSlot->SetAnchors(FAnchors(0.5f, AnchorY));
		TextSlot->SetAlignment(FVector2D(0.5f, AnchorY));
		TextSlot->SetPosition(FVector2D(0.f, OffsetY));
		TextSlot->SetAutoSize(true);
		Block->SetVisibility(ESlateVisibility::HitTestInvisible);
		return Block;
	};
	PointsText = AddText(FText::GetEmpty(), 0.f, 48.f, 24);
	AddText(FText::FromString(TEXT("노드를 눌러 해금  ·  드래그: 이동  ·  휠: 확대/축소  ·  K: 닫기")), 1.f, -40.f, 16);

	Pan = FVector2D::ZeroVector;
	Zoom = Style.InitialZoom;
	ApplyView();

	if (!Skills || !Skills->SkillTable)
	{
		return;
	}

	// 부모 → 자식 목록. 부모가 없거나 표에 없는 스킬은 뿌리.
	TArray<FName> Roots;
	for (const FName& Id : Skills->SkillTable->GetRowNames())
	{
		const FSkillTreeRow* Row = Skills->FindSkill(Id);
		if (Row->Parent.IsNone() || !Skills->FindSkill(Row->Parent))
		{
			Roots.Add(Id);
		}
		else
		{
			Children.FindOrAdd(Row->Parent).Add(Id);
		}
	}

	const float Start = FMath::DegreesToRadians(Style.StartAngle);
	if (Roots.Num() == 1)
	{
		// 뿌리 하나는 화면 가운데, 자식들이 한 바퀴를 나눠 갖는다.
		LayoutBranch(Roots[0], 0, Start - PI, Start + PI);
	}
	else
	{
		// 뿌리가 여럿이면 첫 고리에 둘러 세우고 잎 개수만큼 각도를 나눈다.
		int32 Total = 0;
		for (const FName& Root : Roots)
		{
			Total += CountLeaves(Root);
		}
		float Angle = Start - PI;
		for (const FName& Root : Roots)
		{
			const float Span = 2.f * PI * CountLeaves(Root) / FMath::Max(Total, 1);
			LayoutBranch(Root, 1, Angle, Angle + Span);
			Angle += Span;
		}
	}

	// 선을 먼저 넣어야 노드 아래에 깔린다.
	for (const TPair<FName, TArray<FName>>& Pair : Children)
	{
		for (const FName& Child : Pair.Value)
		{
			if (Positions.Contains(Pair.Key) && Positions.Contains(Child))
			{
				AddLine(Positions[Pair.Key], Positions[Child], Child);
			}
		}
	}
	for (const TPair<FName, FVector2D>& Pair : Positions)
	{
		AddNode(Pair.Key, Pair.Value);
	}
}

int32 USkillTreeWidget::CountLeaves(FName Id) const
{
	const TArray<FName>* Kids = Children.Find(Id);
	if (!Kids || Kids->IsEmpty())
	{
		return 1;
	}
	int32 Count = 0;
	for (const FName& Kid : *Kids)
	{
		Count += CountLeaves(Kid);
	}
	return Count;
}

void USkillTreeWidget::LayoutBranch(FName Id, int32 Depth, float AngleMin, float AngleMax)
{
	if (Positions.Contains(Id))
	{
		return; // 표에 순환 참조가 있어도 멈추게
	}
	const float Angle = (AngleMin + AngleMax) * 0.5f;
	const float Radius = Depth * Skills->Style.RingSpacing;
	Positions.Add(Id, FVector2D(FMath::Cos(Angle), FMath::Sin(Angle)) * Radius);

	const TArray<FName>* Kids = Children.Find(Id);
	if (!Kids)
	{
		return;
	}
	const int32 Total = CountLeaves(Id);
	float AngleCursor = AngleMin;
	for (const FName& Kid : *Kids)
	{
		const float Span = (AngleMax - AngleMin) * CountLeaves(Kid) / Total;
		LayoutBranch(Kid, Depth + 1, AngleCursor, AngleCursor + Span);
		AngleCursor += Span;
	}
}

void USkillTreeWidget::AddLine(const FVector2D& From, const FVector2D& To, FName ChildId)
{
	const FVector2D Delta = To - From;
	UImage* Line = WidgetTree->ConstructWidget<UImage>();
	PlaceCentered(Board, Line, (From + To) * 0.5f, FVector2D(Delta.Size(), Skills->Style.LineThickness));
	Line->SetRenderTransformAngle(FMath::RadiansToDegrees(FMath::Atan2(Delta.Y, Delta.X)));
	Line->SetVisibility(ESlateVisibility::HitTestInvisible);
	LineImages.Add(Line);
	LineChildIds.Add(ChildId);
}

void USkillTreeWidget::AddNode(FName Id, const FVector2D& Position)
{
	const FSkillTreeStyle& Style = Skills->Style;
	const FSkillTreeRow* Row = Skills->FindSkill(Id);

	USkillNodeButton* Button = WidgetTree->ConstructWidget<USkillNodeButton>();
	Button->SkillId = Id;
	Button->Owner = this;
	Button->BindClick();
	Button->SetToolTip(MakeTooltip(Id, *Row));

	if (UTexture2D* Icon = Row->Icon.LoadSynchronous())
	{
		UImage* Image = WidgetTree->ConstructWidget<UImage>();
		Image->SetBrush(MakeBrush(Icon, FVector2D(Style.NodeSize * 0.62f)));
		Button->SetContent(Image);
	}
	else
	{
		UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>();
		Label->SetText(Row->DisplayName);
		Label->SetColorAndOpacity(FSlateColor(Style.TextColor));
		Label->SetJustification(ETextJustify::Center);
		Label->SetAutoWrapText(true);
		FSlateFontInfo Font = Label->GetFont();
		Font.Size = FMath::Max(8, FMath::RoundToInt(Style.NodeSize * 0.15f));
		Label->SetFont(Font);
		Button->SetContent(Label);
	}
	if (UButtonSlot* ContentSlot = Cast<UButtonSlot>(Button->GetContent()->Slot))
	{
		ContentSlot->SetPadding(FMargin(Style.NodeSize * 0.14f));
		ContentSlot->SetHorizontalAlignment(HAlign_Center);
		ContentSlot->SetVerticalAlignment(VAlign_Center);
	}

	PlaceCentered(Board, Button, Position, FVector2D(Style.NodeSize));
	Nodes.Add(Id, Button);
}

UWidget* USkillTreeWidget::MakeTooltip(FName Id, const FSkillTreeRow& Row)
{
	const FSkillTreeStyle& Style = Skills->Style;
	const float Width = Style.TooltipWidth;

	// 바탕: 그림을 위·가운데·아래로 잘라 위아래(장식·도장)는 원래 비율 그대로, 가운데만 세로로 늘린다.
	UOverlay* Panel = WidgetTree->ConstructWidget<UOverlay>();
	if (Style.Tooltip)
	{
		const float Aspect = Style.Tooltip->GetSurfaceHeight() / FMath::Max(1.f, Style.Tooltip->GetSurfaceWidth());
		const float Cap = FMath::Clamp(Style.TooltipSliceMargin, 0.01f, 0.49f);
		UVerticalBox* Frame = WidgetTree->ConstructWidget<UVerticalBox>();
		auto AddPart = [&](float V0, float V1, bool bStretch)
		{
			UImage* Part = WidgetTree->ConstructWidget<UImage>();
			// 가운데 조각은 원하는 높이를 1로 둬서 글이 짧으면 줄어들 수 있게 한다.
			FSlateBrush PartBrush = MakeBrush(Style.Tooltip, FVector2D(Width, bStretch ? 1.f : Width * Aspect * (V1 - V0)));
			PartBrush.SetUVRegion(FBox2f(FVector2f(0.f, V0), FVector2f(1.f, V1)));
			Part->SetBrush(PartBrush);
			if (UVerticalBoxSlot* PartSlot = Frame->AddChildToVerticalBox(Part))
			{
				PartSlot->SetSize(FSlateChildSize(bStretch ? ESlateSizeRule::Fill : ESlateSizeRule::Automatic));
			}
		};
		AddPart(0.f, Cap, false);
		AddPart(Cap, 1.f - Cap, true);
		AddPart(1.f - Cap, 1.f, false);
		UOverlaySlot* FrameSlot = Panel->AddChildToOverlay(Frame);
		FrameSlot->SetHorizontalAlignment(HAlign_Fill);
		FrameSlot->SetVerticalAlignment(VAlign_Fill);
	}
	else
	{
		UImage* Plain = WidgetTree->ConstructWidget<UImage>();
		Plain->SetColorAndOpacity(FLinearColor(0.93f, 0.86f, 0.72f));
		UOverlaySlot* PlainSlot = Panel->AddChildToOverlay(Plain);
		PlainSlot->SetHorizontalAlignment(HAlign_Fill);
		PlainSlot->SetVerticalAlignment(VAlign_Fill);
	}

	UVerticalBox* Lines = WidgetTree->ConstructWidget<UVerticalBox>();
	UOverlaySlot* LinesSlot = Panel->AddChildToOverlay(Lines);
	LinesSlot->SetPadding(Style.TooltipPadding);
	LinesSlot->SetHorizontalAlignment(HAlign_Fill);
	LinesSlot->SetVerticalAlignment(VAlign_Center);

	const float TextWidth = Width - Style.TooltipPadding.Left - Style.TooltipPadding.Right;
	if (Style.TooltipFont && !TooltipComposite.IsValid())
	{
		TSharedRef<FCompositeFont> Composite = MakeShared<FCompositeFont>();
		FTypefaceEntry& Entry = Composite->DefaultTypeface.Fonts.Add_GetRef(FTypefaceEntry(TEXT("Regular")));
		Entry.Font = FFontData(Style.TooltipFont);
		TooltipComposite = Composite;
	}
	auto AddText = [&](const FText& Text, int32 FontSize, float Gap) -> UTextBlock*
	{
		UTextBlock* Block = WidgetTree->ConstructWidget<UTextBlock>();
		Block->SetText(Text);
		Block->SetColorAndOpacity(FSlateColor(Style.TextColor));
		Block->SetAutoWrapText(true);
		Block->SetWrapTextAt(TextWidth);
		FSlateFontInfo Font = TooltipComposite.IsValid() ? FSlateFontInfo(TooltipComposite, FontSize) : Block->GetFont();
		Font.Size = FontSize;
		Block->SetFont(Font);
		if (UVerticalBoxSlot* LineSlot = Lines->AddChildToVerticalBox(Block))
		{
			LineSlot->SetPadding(FMargin(0.f, 0.f, 0.f, Gap));
		}
		return Block;
	};
	AddText(Row.DisplayName, Style.TooltipFontSizes.X, 2.f);
	TooltipStatus.Add(Id, AddText(FText::GetEmpty(), Style.TooltipFontSizes.Y, 8.f));
	AddText(Row.Description, Style.TooltipFontSizes.Z, 0.f);

	USizeBox* Box = WidgetTree->ConstructWidget<USizeBox>();
	Box->SetWidthOverride(Width);
	Box->SetContent(Panel);
	return Box;
}

void USkillTreeWidget::Refresh()
{
	if (!Skills)
	{
		return;
	}
	const FSkillTreeStyle& Style = Skills->Style;

	if (PointsText)
	{
		PointsText->SetText(FText::Format(FText::FromString(TEXT("스킬 포인트  {0}")), FText::AsNumber(Skills->SkillPoints)));
	}

	const FVector2D NodeSize(Style.NodeSize);
	for (const TPair<FName, TObjectPtr<USkillNodeButton>>& Pair : Nodes)
	{
		const bool bUnlocked = Skills->IsUnlocked(Pair.Key);
		const bool bAvailable = !bUnlocked && Skills->CanUnlock(Pair.Key);
		UTexture2D* Normal = bUnlocked ? Style.NodeUnlocked : (bAvailable ? Style.NodeAvailable : Style.NodeLocked);
		UTexture2D* Hover = (bUnlocked || bAvailable) ? Style.NodeSelected : Style.NodeLocked;

		FButtonStyle ButtonStyle;
		ButtonStyle.SetNormal(MakeBrush(Normal, NodeSize));
		ButtonStyle.SetHovered(MakeBrush(Hover, NodeSize));
		ButtonStyle.SetPressed(MakeBrush(Hover, NodeSize));
		ButtonStyle.SetDisabled(MakeBrush(Normal, NodeSize));
		ButtonStyle.SetNormalPadding(FMargin(0.f));
		ButtonStyle.SetPressedPadding(FMargin(0.f));
		Pair.Value->SetStyle(ButtonStyle);
		Pair.Value->SetRenderOpacity(bUnlocked || bAvailable ? 1.f : 0.75f);

		if (UTextBlock* Status = TooltipStatus.FindRef(Pair.Key))
		{
			const FSkillTreeRow* Row = Skills->FindSkill(Pair.Key);
			const FSkillTreeRow* ParentRow = Row ? Skills->FindSkill(Row->Parent) : nullptr;
			FText State;
			FLinearColor Color;
			if (bUnlocked)
			{
				State = FText::FromString(TEXT("해금됨"));
				Color = FLinearColor(0.62f, 0.45f, 0.12f);
			}
			else if (bAvailable)
			{
				State = FText::FromString(TEXT("해금 가능"));
				Color = Style.TextColor;
			}
			else if (ParentRow && !Skills->IsUnlocked(Row->Parent))
			{
				State = FText::Format(FText::FromString(TEXT("먼저 '{0}' 해금 필요")), ParentRow->DisplayName);
				Color = FLinearColor(0.45f, 0.1f, 0.08f);
			}
			else
			{
				State = FText::FromString(TEXT("포인트 부족"));
				Color = FLinearColor(0.45f, 0.1f, 0.08f);
			}
			Status->SetText(FText::Format(FText::FromString(TEXT("비용 {0}  /  {1}")), FText::AsNumber(Row ? Row->Cost : 0), State));
			Status->SetColorAndOpacity(FSlateColor(Color));
		}
	}

	for (int32 i = 0; i < LineImages.Num(); ++i)
	{
		UTexture2D* Texture = Skills->IsUnlocked(LineChildIds[i]) ? Style.LineActive : Style.LineInactive;
		// 선 그림의 높이를 선 두께에 맞추고 가로로 반복해 늘어나도 무늬가 유지되게 한다.
		const float Height = Texture ? FMath::Max(1.f, Texture->GetSurfaceHeight()) : 1.f;
		const float Width = Texture ? Texture->GetSurfaceWidth() * Style.LineThickness / Height : 1.f;
		FSlateBrush Brush = MakeBrush(Texture, FVector2D(Width, Style.LineThickness));
		Brush.Tiling = ESlateBrushTileType::Horizontal;
		LineImages[i]->SetBrush(Brush);
	}
}
