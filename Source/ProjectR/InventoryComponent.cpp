#include "InventoryComponent.h"

#include "Engine/DataTable.h"
#include "Engine/GameInstance.h"
#include "PlayerSkillComponent.h"
#include "PlayerStatsComponent.h"
#include "ProjectRCharacter.h"
#include "RunSubsystem.h"

UInventoryComponent::UInventoryComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	StartItems = { { TEXT("Potion"), 3 }, { TEXT("ManaPotion"), 3 } };
}

void UInventoryComponent::BeginPlay()
{
	Super::BeginPlay();

	UPlayerSkillComponent* Skills = GetOwner()->FindComponentByClass<UPlayerSkillComponent>();
	const URunSubsystem* Run = GetWorld()->GetGameInstance() ? GetWorld()->GetGameInstance()->GetSubsystem<URunSubsystem>() : nullptr;
	if (Run && Run->bHasInventory)
	{
		Bag = Run->SavedBag;
		if (Skills)
		{
			Skills->GemSkills = Run->SavedGems;
		}
	}
	else
	{
		Bag = StartItems;
	}
	Bag.SetNum(BagSize);
	Save();
}

AProjectRCharacter* UInventoryComponent::GetCharacter() const
{
	return Cast<AProjectRCharacter>(GetOwner());
}

const FItemRow* UInventoryComponent::FindItem(FName ItemId) const
{
	const UDataTable* Table = ItemTable.LoadSynchronous();
	return Table && !ItemId.IsNone() ? Table->FindRow<FItemRow>(ItemId, TEXT("Inventory"), false) : nullptr;
}

bool UInventoryComponent::IsGemRef(int32 SlotRef) const
{
	const int32 GemIndex = GemIndexOf(SlotRef);
	return SlotRef <= GemSlotRef(0) && GemIndex < UPlayerSkillComponent::GemSlotCount;
}

FInventoryStack UInventoryComponent::GetSlot(int32 SlotRef) const
{
	if (IsBagRef(SlotRef))
	{
		return Bag[SlotRef];
	}
	if (SlotRef == WeaponSlotRef)
	{
		const AProjectRCharacter* Character = GetCharacter();
		const FName Weapon = Character ? Character->GetCurrentWeapon() : NAME_None;
		return { Weapon, Weapon.IsNone() ? 0 : 1 };
	}
	if (IsGemRef(SlotRef))
	{
		const UPlayerSkillComponent* Skills = GetOwner()->FindComponentByClass<UPlayerSkillComponent>();
		const FName Gem = Skills ? Skills->GetSlotSkill(GemIndexOf(SlotRef)) : NAME_None;
		return { Gem, Gem.IsNone() ? 0 : 1 };
	}
	return {};
}

int32 UInventoryComponent::FindEmptyBagSlot() const
{
	return Bag.IndexOfByPredicate([](const FInventoryStack& Stack) { return Stack.IsEmpty(); });
}

bool UInventoryComponent::AddItem(FName ItemId, int32 Count)
{
	const FItemRow* Row = FindItem(ItemId);
	if (!Row || Count <= 0)
	{
		return false;
	}
	// 남은 개수가 다 들어갈 자리가 있는지 먼저 센다(반만 들어가는 일 없게).
	int32 Room = 0;
	for (const FInventoryStack& Stack : Bag)
	{
		Room += Stack.IsEmpty() ? Row->MaxStack : (Stack.ItemId == ItemId ? FMath::Max(0, Row->MaxStack - Stack.Count) : 0);
	}
	if (Room < Count)
	{
		return false;
	}
	for (FInventoryStack& Stack : Bag)
	{
		if (Count > 0 && !Stack.IsEmpty() && Stack.ItemId == ItemId)
		{
			const int32 Moved = FMath::Min(Count, Row->MaxStack - Stack.Count);
			Stack.Count += Moved;
			Count -= Moved;
		}
	}
	for (FInventoryStack& Stack : Bag)
	{
		if (Count > 0 && Stack.IsEmpty())
		{
			const int32 Moved = FMath::Min(Count, Row->MaxStack);
			Stack = { ItemId, Moved };
			Count -= Moved;
		}
	}
	Save();
	return true;
}

void UInventoryComponent::SetGem(int32 GemIndex, FName ItemId)
{
	if (UPlayerSkillComponent* Skills = GetOwner()->FindComponentByClass<UPlayerSkillComponent>())
	{
		Skills->GemSkills.SetNum(UPlayerSkillComponent::GemSlotCount);
		Skills->GemSkills[GemIndex] = ItemId;
	}
}

bool UInventoryComponent::MoveItem(int32 FromRef, int32 ToRef)
{
	const FInventoryStack From = GetSlot(FromRef);
	const FInventoryStack To = GetSlot(ToRef);
	const FItemRow* FromRow = FindItem(From.ItemId);
	const FItemRow* ToRow = FindItem(To.ItemId);
	if (FromRef == ToRef || From.IsEmpty() || !FromRow)
	{
		return false;
	}

	auto Kind = [](const FItemRow* Row, EItemKind K) { return Row && Row->Kind == K; };
	bool bDone = false;

	if (IsBagRef(FromRef) && IsBagRef(ToRef))
	{
		if (To.ItemId == From.ItemId && FromRow->MaxStack > 1)
		{
			const int32 Moved = FMath::Min(From.Count, FromRow->MaxStack - To.Count);
			Bag[ToRef].Count += Moved;
			Bag[FromRef].Count -= Moved;
			if (Bag[FromRef].Count <= 0)
			{
				Bag[FromRef] = {};
			}
		}
		else
		{
			Bag.Swap(FromRef, ToRef);
		}
		bDone = true;
	}
	else if (IsBagRef(FromRef) || IsBagRef(ToRef))
	{
		// 가방 칸 하나와 장착칸 하나: 장착칸 쪽으로 정리한다.
		const int32 BagRef = IsBagRef(FromRef) ? FromRef : ToRef;
		const int32 EquipRef = IsBagRef(FromRef) ? ToRef : FromRef;
		const FInventoryStack BagStack = Bag[BagRef];
		const FItemRow* BagRow = FindItem(BagStack.ItemId);
		const FInventoryStack Equipped = GetSlot(EquipRef);

		if (EquipRef == WeaponSlotRef)
		{
			// 무기 칸은 비울 수 없다: 가방의 무기와 맞바꾸기만 한다.
			AProjectRCharacter* Character = GetCharacter();
			if (Character && Kind(BagRow, EItemKind::Weapon) && BagStack.ItemId != Equipped.ItemId)
			{
				Character->EquipWeapon(BagStack.ItemId);
				Bag[BagRef] = Equipped.IsEmpty() ? FInventoryStack() : FInventoryStack{ Equipped.ItemId, 1 };
				bDone = true;
			}
		}
		else if (IsGemRef(EquipRef) && (BagStack.IsEmpty() || Kind(BagRow, EItemKind::Gem)))
		{
			// 빈 가방 칸이면 해제, 젬이면 맞바꾸기
			if (!(BagStack.IsEmpty() && Equipped.IsEmpty()))
			{
				SetGem(GemIndexOf(EquipRef), BagStack.ItemId);
				Bag[BagRef] = Equipped.IsEmpty() ? FInventoryStack() : FInventoryStack{ Equipped.ItemId, 1 };
				bDone = true;
			}
		}
	}
	else if (IsGemRef(FromRef) && IsGemRef(ToRef))
	{
		SetGem(GemIndexOf(ToRef), From.ItemId);
		SetGem(GemIndexOf(FromRef), To.ItemId);
		bDone = true;
	}

	if (bDone)
	{
		Save();
	}
	return bDone;
}

bool UInventoryComponent::Drink(int32 BagIndex)
{
	const FItemRow* Row = FindItem(Bag[BagIndex].ItemId);
	UPlayerStatsComponent* Stats = GetOwner()->FindComponentByClass<UPlayerStatsComponent>();
	if (!Row || !Stats || Row->Kind != EItemKind::Consumable)
	{
		return false;
	}
	Stats->Heal(Row->HealthRestore);
	Stats->RestoreMana(Row->ManaRestore);
	if (--Bag[BagIndex].Count <= 0)
	{
		Bag[BagIndex] = {};
	}
	Save();
	return true;
}

bool UInventoryComponent::QuickUse(int32 SlotRef)
{
	const FInventoryStack Stack = GetSlot(SlotRef);
	const FItemRow* Row = FindItem(Stack.ItemId);
	if (Stack.IsEmpty() || !Row)
	{
		return false;
	}
	if (IsBagRef(SlotRef))
	{
		switch (Row->Kind)
		{
		case EItemKind::Consumable:
			return Drink(SlotRef);
		case EItemKind::Weapon:
			return MoveItem(SlotRef, WeaponSlotRef);
		case EItemKind::Gem:
			for (int32 i = 0; i < UPlayerSkillComponent::GemSlotCount; ++i)
			{
				if (GetSlot(GemSlotRef(i)).IsEmpty())
				{
					return MoveItem(SlotRef, GemSlotRef(i));
				}
			}
			return false;
		}
	}
	if (IsGemRef(SlotRef))
	{
		const int32 Empty = FindEmptyBagSlot();
		return Empty != INDEX_NONE && MoveItem(SlotRef, Empty);
	}
	return false;
}

void UInventoryComponent::Save()
{
	if (URunSubsystem* Run = GetWorld()->GetGameInstance() ? GetWorld()->GetGameInstance()->GetSubsystem<URunSubsystem>() : nullptr)
	{
		Run->bHasInventory = true;
		Run->SavedBag = Bag;
		if (const UPlayerSkillComponent* Skills = GetOwner()->FindComponentByClass<UPlayerSkillComponent>())
		{
			Run->SavedGems = Skills->GemSkills;
		}
	}
	OnChanged.Broadcast();
}
