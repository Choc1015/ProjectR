#include "RoomMapWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/ScaleBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Engine/FontFace.h"
#include "Engine/Texture2D.h"
#include "Fonts/CompositeFont.h"
#include "RunSettings.h"
#include "RunSubsystem.h"

namespace
{
	FSlateBrush MakeBrush(UTexture2D* Texture, const FVector2D& Size)
	{
		FSlateBrush Brush;
		Brush.DrawAs = ESlateBrushDrawType::Image;
		Brush.SetResourceObject(Texture);
		Brush.ImageSize = Size;
		return Brush;
	}
}

void URoomMapNodeButton::BindClick()
{
	OnClicked.AddUniqueDynamic(this, &URoomMapNodeButton::HandleClicked);
}

void URoomMapNodeButton::HandleClicked()
{
	if (URoomMapWidget* Widget = Owner.Get())
	{
		Widget->OnNodeClicked(NodeIndex);
	}
}

void URoomMapWidget::Init(URunSubsystem* InRun)
{
	Run = InRun;
	SetIsFocusable(true);
	Build();
}

void URoomMapWidget::OnNodeClicked(int32 NodeIndex)
{
	if (Run && Run->IsReachable(NodeIndex))
	{
		Run->TravelTo(NodeIndex);
	}
}

FReply URoomMapWidget::NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent)
{
	if (InKeyEvent.GetKey() == EKeys::Escape && Run)
	{
		Run->CloseMap();
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
}

void URoomMapWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	const URunSettings* Settings = GetDefault<URunSettings>();
	Time += InDeltaTime;
	const float Scale = 1.f + Settings->PulseScale * 0.5f * (1.f + FMath::Sin(Time * Settings->PulseSpeed * UE_TWO_PI));
	for (URoomMapNodeButton* Node : PulseNodes)
	{
		if (Node && !Node->IsHovered())
		{
			Node->SetRenderScale(FVector2D(Scale));
		}
		else if (Node)
		{
			Node->SetRenderScale(FVector2D(1.f + Settings->PulseScale * 1.5f));
		}
	}
}

FVector2D URoomMapWidget::NodePosition(int32 NodeIndex) const
{
	const URunSettings* Settings = GetDefault<URunSettings>();
	const FRunMapNode& Node = Run->GetNodes()[NodeIndex];
	const FVector2D Size = Settings->BoardSize;
	const double Left = Settings->NodeArea.X * Size.X;
	const double Top = Settings->NodeArea.Y * Size.Y;
	const double Width = (Settings->NodeArea.Z - Settings->NodeArea.X) * Size.X;
	const double Height = (Settings->NodeArea.W - Settings->NodeArea.Y) * Size.Y;
	const int32 Rows = FMath::Max(1, Settings->Rows);
	const int32 Columns = FMath::Max(1, Settings->Columns);
	const double CellW = Width / Columns;
	const double CellH = Height / Rows;

	// 시작 칸은 맨 아래 가운데, 나머지는 열 칸 가운데에 두고 조금씩 흔든다.
	const double X = Node.Row == 0 ? Left + Width * 0.5 : Left + CellW * (Node.Column + 0.5 + Node.Jitter.X);
	const double Y = Top + Height - CellH * (Node.Row + Node.Jitter.Y);
	return FVector2D(X, Y);
}

void URoomMapWidget::AddDashedLine(const FVector2D& From, const FVector2D& To)
{
	const URunSettings* Settings = GetDefault<URunSettings>();
	const double DashLength = Settings->DashLengthGapThickness.X;
	const double Gap = Settings->DashLengthGapThickness.Y;
	const double Thickness = Settings->DashLengthGapThickness.Z;

	const FVector2D Delta = To - From;
	const double Length = Delta.Size();
	const double Margin = Settings->NodeSize * 0.6;
	if (Length <= Margin * 2.0)
	{
		return;
	}
	const FVector2D Dir = Delta / Length;
	const float Angle = FMath::RadiansToDegrees(FMath::Atan2(Dir.Y, Dir.X));

	for (double D = Margin; D + DashLength <= Length - Margin; D += DashLength + Gap)
	{
		UImage* Dash = WidgetTree->ConstructWidget<UImage>();
		Dash->SetColorAndOpacity(Settings->InkColor);
		Dash->SetVisibility(ESlateVisibility::HitTestInvisible);
		Dash->SetRenderTransformAngle(Angle);
		UCanvasPanelSlot* CSlot = Board->AddChildToCanvas(Dash);
		CSlot->SetAlignment(FVector2D(0.5, 0.5));
		CSlot->SetSize(FVector2D(DashLength, Thickness));
		CSlot->SetPosition(From + Dir * (D + DashLength * 0.5));
	}
}

void URoomMapWidget::Build()
{
	const URunSettings* Settings = GetDefault<URunSettings>();
	const TArray<FRunMapNode>& Nodes = Run->GetNodes();
	const int32 Current = Run->GetCurrentNode();

	if (UFontFace* FontFace = Settings->Font.LoadSynchronous())
	{
		TSharedRef<FCompositeFont> Composite = MakeShared<FCompositeFont>();
		FTypefaceEntry& Entry = Composite->DefaultTypeface.Fonts.Add_GetRef(FTypefaceEntry(TEXT("Regular")));
		Entry.Font = FFontData(FontFace);
		Font = Composite;
		FontAsset = FontFace;
	}

	// 게임 화면을 완전히 가린다. 지도 판(원본 배경 그림 그대로)이 화면을 꽉 채우고, 비율이 달라 남는 곳은 판 가장자리 색으로 메운다.
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Root;

	UImage* Cover = WidgetTree->ConstructWidget<UImage>();
	Cover->SetColorAndOpacity(Settings->CoverColor);
	UCanvasPanelSlot* CoverSlot = Root->AddChildToCanvas(Cover);
	CoverSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	CoverSlot->SetOffsets(FMargin(0.f));

	UScaleBox* Fit = WidgetTree->ConstructWidget<UScaleBox>();
	Fit->SetStretch(EStretch::ScaleToFill);
	UCanvasPanelSlot* FitSlot = Root->AddChildToCanvas(Fit);
	FitSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	FitSlot->SetOffsets(FMargin(0.f));

	USizeBox* BoardBox = WidgetTree->ConstructWidget<USizeBox>();
	BoardBox->SetWidthOverride(Settings->BoardSize.X);
	BoardBox->SetHeightOverride(Settings->BoardSize.Y);
	Fit->AddChild(BoardBox);

	Board = WidgetTree->ConstructWidget<UCanvasPanel>();
	BoardBox->AddChild(Board);

	UImage* Backdrop = WidgetTree->ConstructWidget<UImage>();
	Backdrop->SetBrush(MakeBrush(Settings->Backdrop.LoadSynchronous(), Settings->BoardSize));
	UCanvasPanelSlot* BackdropSlot = Board->AddChildToCanvas(Backdrop);
	BackdropSlot->SetAnchors(FAnchors(0.f, 0.f, 1.f, 1.f));
	BackdropSlot->SetOffsets(FMargin(0.f));

	auto AddText = [&](const FText& Text, int32 Size, const FVector2D& Position)
	{
		UTextBlock* Block = WidgetTree->ConstructWidget<UTextBlock>();
		Block->SetText(Text);
		Block->SetColorAndOpacity(FSlateColor(Settings->InkColor.CopyWithNewOpacity(1.f)));
		Block->SetJustification(ETextJustify::Center);
		Block->SetVisibility(ESlateVisibility::HitTestInvisible);
		FSlateFontInfo FontInfo = Font.IsValid() ? FSlateFontInfo(Font, Size) : Block->GetFont();
		FontInfo.Size = Size;
		Block->SetFont(FontInfo);
		UCanvasPanelSlot* CSlot = Board->AddChildToCanvas(Block);
		CSlot->SetAutoSize(true);
		CSlot->SetAlignment(FVector2D(0.5, 0.0));
		CSlot->SetPosition(Position);
	};

	AddText(FText::FromString(TEXT("다음 방을 고르세요")), Settings->TitleFontSize, FVector2D(Settings->BoardSize.X * 0.5, Settings->BoardSize.Y * 0.05));
	AddText(FText::FromString(TEXT("Esc: 닫기")), Settings->LabelFontSize, Settings->BoardSize * Settings->CloseHintPosition);

	// 길 먼저, 칸은 그 위에
	for (int32 i = 0; i < Nodes.Num(); ++i)
	{
		for (int32 Next : Nodes[i].Next)
		{
			AddDashedLine(NodePosition(i), NodePosition(Next));
		}
	}

	UTexture2D* RoomTexture = Settings->NodeRoom.LoadSynchronous();
	UTexture2D* StartTexture = Settings->NodeStart.LoadSynchronous();
	UTexture2D* CurrentTexture = Settings->NodeCurrent.LoadSynchronous();
	UTexture2D* CrossTexture = Settings->VisitedMark.LoadSynchronous();
	const FVector2D NodeSize(Settings->NodeSize);

	for (int32 i = 0; i < Nodes.Num(); ++i)
	{
		const FRunMapNode& Node = Nodes[i];
		const bool bCurrent = i == Current;
		const bool bReachable = Run->IsReachable(i);
		UTexture2D* Texture = bCurrent ? CurrentTexture : (Node.Row == 0 ? StartTexture : RoomTexture);

		URoomMapNodeButton* Button = WidgetTree->ConstructWidget<URoomMapNodeButton>();
		Button->NodeIndex = i;
		Button->Owner = this;
		Button->BindClick();
		FButtonStyle Style;
		const FSlateBrush Brush = MakeBrush(Texture, NodeSize);
		Style.SetNormal(Brush);
		Style.SetHovered(Brush);
		Style.SetPressed(Brush);
		Style.SetDisabled(Brush);
		Style.SetNormalPadding(FMargin(0.f));
		Style.SetPressedPadding(FMargin(0.f));
		Button->SetStyle(Style);
		Button->SetRenderTransformPivot(FVector2D(0.5, 0.5));
		if (!bReachable && !bCurrent)
		{
			Button->SetRenderOpacity(Node.bVisited ? 0.85f : Settings->LockedOpacity);
		}
		if (bReachable)
		{
			PulseNodes.Add(Button);
			Button->SetCursor(EMouseCursor::Hand);
		}

		const FVector2D Position = NodePosition(i);
		UCanvasPanelSlot* CSlot = Board->AddChildToCanvas(Button);
		CSlot->SetAlignment(FVector2D(0.5, 0.5));
		CSlot->SetSize(NodeSize);
		CSlot->SetPosition(Position);

		if (Node.bVisited && CrossTexture)
		{
			UImage* Cross = WidgetTree->ConstructWidget<UImage>();
			Cross->SetBrush(MakeBrush(CrossTexture, NodeSize * 0.9));
			Cross->SetVisibility(ESlateVisibility::HitTestInvisible);
			UCanvasPanelSlot* CrossSlot = Board->AddChildToCanvas(Cross);
			CrossSlot->SetAlignment(FVector2D(0.5, 0.5));
			CrossSlot->SetSize(NodeSize * 0.9);
			CrossSlot->SetPosition(Position);
		}

		// 갈 수 있는 칸과 지금 칸에만 방 이름을 단다(전부 달면 지도가 글로 덮인다).
		if ((bReachable || bCurrent) && Settings->Rooms.IsValidIndex(Node.RoomIndex))
		{
			AddText(Settings->Rooms[Node.RoomIndex].DisplayName, Settings->LabelFontSize, Position + FVector2D(0.0, Settings->NodeSize * 0.55));
		}
	}
}
