#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ItemTypes.h"
#include "InventoryComponent.generated.h"

class AProjectRCharacter;
class UDataTable;
class UFontFace;
class UTexture2D;

/** 인벤토리 창의 그림·배치 수치. 좌표는 판(BoardSize) 기준 픽셀 */
USTRUCT(BlueprintType)
struct FInventoryStyle
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Texture")
	TSoftObjectPtr<UTexture2D> Backdrop = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Inventory/T_InventoryBackdrop.T_InventoryBackdrop")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Texture")
	TSoftObjectPtr<UTexture2D> SlotFrame = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Inventory/T_InvSlot.T_InvSlot")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Texture")
	TSoftObjectPtr<UTexture2D> WeaponSlotFrame = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Inventory/T_InvWeaponSlot.T_InvWeaponSlot")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Texture")
	TSoftObjectPtr<UTexture2D> GemSlotFrame = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Inventory/T_InvGemSlot.T_InvGemSlot")));

	/** 마우스를 올린 칸에 겹치는 금박 테두리 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Texture")
	TSoftObjectPtr<UTexture2D> HoverFrame = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Inventory/T_InvSelect.T_InvSelect")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	TSoftObjectPtr<UFontFace> Font = TSoftObjectPtr<UFontFace>(FSoftObjectPath(TEXT("/Game/UI/Fonts/FF_NanumPenScript.FF_NanumPenScript")));

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	FLinearColor InkColor = FLinearColor(0.16f, 0.09f, 0.04f, 1.f);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	int32 TitleFontSize = 40;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	int32 TextFontSize = 26;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Text")
	int32 CountFontSize = 24;

	/** 화면을 덮는 바탕색 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	FLinearColor CoverColor = FLinearColor::Black;

	/** 일지 그림 크기. 화면 비율에 맞춰 통째로 늘고 준다 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	FVector2D BoardSize = FVector2D(1600.0, 893.0);

	/** 왼쪽(장비)·오른쪽(가방) 쪽 가운데 X */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	FVector2D PageCenterX = FVector2D(450.0, 1155.0);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float TitleY = 110.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float WeaponSlotSize = 170.f;

	/** 무기 칸 가운데 Y */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float WeaponSlotY = 290.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float GemSlotSize = 110.f;

	/** 젬 칸 가운데 Y와 칸 사이 거리 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	FVector2D GemSlotYSpacing = FVector2D(500.0, 140.0);

	/** 마우스를 올린 아이템 이름·설명 위치(Y)와 글 너비 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	FVector2D InfoYWidth = FVector2D(625.0, 560.0);

	/** 가방 칸 크기·칸 사이 틈 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	FVector2D BagCellGap = FVector2D(104.0, 8.0);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	int32 BagColumns = 5;

	/** 가방 칸 맨 윗줄 위 끝 Y */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float BagTop = 190.f;

	/** 조작 안내 글 Y */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout")
	float HintY = 720.f;

	/** 칸 안 아이콘 여백(칸 크기 비율) */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Layout", meta = (ClampMin = "0", ClampMax = "0.45"))
	float IconPadding = 0.14f;
};

DECLARE_MULTICAST_DELEGATE(FOnInventoryChanged);

/**
 * 가방(포션·젬·무기)과 장착칸(무기 1, 젬 Q·E·R). 런 동안 방을 옮겨도 URunSubsystem에 남는다.
 * 칸 번호: 0 이상 = 가방, WeaponSlotRef = 무기 칸, GemSlotRef(i) = 젬 칸
 */
UCLASS(ClassGroup = (ProjectR), meta = (BlueprintSpawnableComponent))
class PROJECTR_API UInventoryComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	static constexpr int32 WeaponSlotRef = -1;
	static int32 GemSlotRef(int32 GemIndex) { return -2 - GemIndex; }
	static int32 GemIndexOf(int32 SlotRef) { return -2 - SlotRef; }

	UInventoryComponent();

	/** 아이템 표. 원본 SourceArt/Data/Items.csv */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Inventory")
	TSoftObjectPtr<UDataTable> ItemTable = TSoftObjectPtr<UDataTable>(FSoftObjectPath(TEXT("/Game/Data/DT_Items.DT_Items")));

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Inventory", meta = (ClampMin = "1"))
	int32 BagSize = 20;

	/** 런을 처음 시작할 때 가방에 넣어 두는 아이템 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Inventory")
	TArray<FInventoryStack> StartItems;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Inventory")
	FInventoryStyle Style;

	FOnInventoryChanged OnChanged;

	const FItemRow* FindItem(FName ItemId) const;

	/** 칸에 든 아이템(장착칸 포함). 비었으면 Count 0 */
	FInventoryStack GetSlot(int32 SlotRef) const;
	const TArray<FInventoryStack>& GetBag() const { return Bag; }

	/** 겹칠 수 있는 칸에 먼저 넣고 남으면 빈 칸에. 다 넣으면 true */
	bool AddItem(FName ItemId, int32 Count = 1);

	/** 끌어다 놓기: 장착·해제·자리 바꾸기·겹치기 */
	bool MoveItem(int32 FromRef, int32 ToRef);

	/** 우클릭: 포션은 마시고, 가방의 젬·무기는 장착, 장착한 젬은 가방으로 */
	bool QuickUse(int32 SlotRef);

protected:
	virtual void BeginPlay() override;

private:
	bool IsBagRef(int32 SlotRef) const { return Bag.IsValidIndex(SlotRef); }
	bool IsGemRef(int32 SlotRef) const;
	int32 FindEmptyBagSlot() const;
	bool Drink(int32 BagIndex);
	void SetGem(int32 GemIndex, FName ItemId);
	void Save();

	AProjectRCharacter* GetCharacter() const;

	UPROPERTY(Transient)
	TArray<FInventoryStack> Bag;
};
