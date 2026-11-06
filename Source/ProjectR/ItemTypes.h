#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "ItemTypes.generated.h"

class UTexture2D;

UENUM(BlueprintType)
enum class EItemKind : uint8
{
	Consumable	UMETA(DisplayName = "소모품"),
	Gem			UMETA(DisplayName = "젬"),
	Weapon		UMETA(DisplayName = "무기")
};

/**
 * 아이템 표(DT_Items) 한 줄. 원본 SourceArt/Data/Items.csv.
 * 행 이름 = 아이템 ID. 젬은 스킬 표 ID, 무기는 무기 표 ID와 같게 둔다.
 */
USTRUCT(BlueprintType)
struct FItemRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item")
	EItemKind Kind = EItemKind::Consumable;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item")
	TSoftObjectPtr<UTexture2D> Icon;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item", meta = (MultiLine = true))
	FText Description;

	/** 한 칸에 겹칠 수 있는 개수 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item", meta = (ClampMin = "1"))
	int32 MaxStack = 1;

	/** 소모품: 마시면 회복하는 체력 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item|Consumable", meta = (ClampMin = "0"))
	float HealthRestore = 0.f;

	/** 소모품: 마시면 회복하는 마나 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item|Consumable", meta = (ClampMin = "0"))
	float ManaRestore = 0.f;
};

/** 가방 한 칸. ItemId가 None이면 빈 칸 */
USTRUCT(BlueprintType)
struct FInventoryStack
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item")
	FName ItemId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item", meta = (ClampMin = "0"))
	int32 Count = 0;

	bool IsEmpty() const { return ItemId.IsNone() || Count <= 0; }
};
