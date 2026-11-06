#pragma once

#include "CoreMinimal.h"
#include "Blueprint/DragDropOperation.h"
#include "Blueprint/UserWidget.h"
#include "InventoryComponent.h"
#include "InventoryWidget.generated.h"

class UCanvasPanel;
class UImage;
class UTextBlock;
class UInventoryWidget;
class AProjectRCharacter;
struct FCompositeFont;

/** 끌고 있는 칸 번호 */
UCLASS()
class PROJECTR_API UInventoryDragOperation : public UDragDropOperation
{
	GENERATED_BODY()

public:
	int32 FromRef = 0;
};

/** 칸 하나(가방·장착칸 공용): 틀 + 아이콘 + 개수. 끌어다 놓기·우클릭·마우스 올리기를 받는다. */
UCLASS()
class PROJECTR_API UInventorySlotWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void Setup(UInventoryWidget* InOwner, int32 InSlotRef, UTexture2D* Frame, float Size);
	void Refresh();
	int32 GetSlotRef() const { return SlotRef; }

protected:
	virtual FReply NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual void NativeOnDragDetected(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent, UDragDropOperation*& OutOperation) override;
	virtual bool NativeOnDrop(const FGeometry& InGeometry, const FDragDropEvent& InDragDropEvent, UDragDropOperation* InOperation) override;
	virtual void NativeOnMouseEnter(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual void NativeOnMouseLeave(const FPointerEvent& InMouseEvent) override;

private:
	TWeakObjectPtr<UInventoryWidget> Owner;
	int32 SlotRef = 0;
	float SlotSize = 100.f;

	UPROPERTY(Transient)
	TObjectPtr<UImage> Icon;

	UPROPERTY(Transient)
	TObjectPtr<UImage> Hover;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> CountText;
};

/**
 * I로 여는 인벤토리 창(코드로 생성). 화면을 검게 덮고 찢어진 일지 위에 왼쪽 장비칸, 오른쪽 가방 칸.
 * 열려 있는 동안 게임은 멈추고, I나 Esc로 닫는다. 그림·배치는 인벤토리 컴포넌트의 Style.
 */
UCLASS()
class PROJECTR_API UInventoryWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void Init(AProjectRCharacter* InCharacter, UInventoryComponent* InInventory);

	UInventoryComponent* GetInventory() const { return Inventory; }
	const FInventoryStyle& GetStyle() const { return Inventory->Style; }
	FSlateFontInfo MakeFont(int32 Size) const;

	void ShowInfo(int32 SlotRef);
	void HideInfo(int32 SlotRef);

protected:
	virtual FReply NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override;
	virtual void NativeDestruct() override;

private:
	void Build();
	void RefreshAll();
	UTextBlock* AddText(const FText& Text, int32 Size, const FVector2D& Position, float WrapWidth = 0.f);
	void AddSlot(int32 SlotRef, UTexture2D* Frame, float Size, const FVector2D& Center);

	TWeakObjectPtr<AProjectRCharacter> Character;

	UPROPERTY(Transient)
	TObjectPtr<UInventoryComponent> Inventory;

	UPROPERTY(Transient)
	TObjectPtr<UCanvasPanel> Board;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UInventorySlotWidget>> Slots;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> InfoName;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> InfoText;

	TSharedPtr<const FCompositeFont> Font;

	UPROPERTY(Transient)
	TObjectPtr<UObject> FontAsset;

	int32 InfoSlotRef = TNumericLimits<int32>::Min();
	FDelegateHandle ChangedHandle;
};
