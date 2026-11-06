#include "RunSubsystem.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Engine/GameInstance.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "RoomExitDoor.h"
#include "RoomMapWidget.h"
#include "RunSettings.h"

void URunSubsystem::EnsureRun()
{
	if (Nodes.Num() == 0)
	{
		Generate();
	}
}

void URunSubsystem::Generate()
{
	const URunSettings* Settings = GetDefault<URunSettings>();
	const int32 Rows = FMath::Max(1, Settings->Rows);
	const int32 Columns = FMath::Max(1, Settings->Columns);
	const int32 RoomCount = Settings->Rooms.Num();

	Nodes.Reset();
	TMap<FIntPoint, int32> Grid;

	FRunMapNode& Start = Nodes.AddDefaulted_GetRef();
	Start.Column = Columns / 2;
	Start.RoomIndex = FMath::Clamp(Settings->StartRoomIndex, 0, FMath::Max(0, RoomCount - 1));
	CurrentNode = 0;

	auto GetOrAdd = [&](int32 Row, int32 Column) -> int32
	{
		if (const int32* Found = Grid.Find(FIntPoint(Row, Column)))
		{
			return *Found;
		}
		FRunMapNode& Node = Nodes.AddDefaulted_GetRef();
		Node.Row = Row;
		Node.Column = Column;
		Node.Jitter = FVector2D(FMath::FRandRange(-0.22f, 0.22f), FMath::FRandRange(-0.18f, 0.18f));
		return Grid.Add(FIntPoint(Row, Column), Nodes.Num() - 1);
	};

	// 길마다 시작 열을 되도록 다르게 고른다.
	TArray<int32> StartColumns;
	for (int32 c = 0; c < Columns; ++c)
	{
		StartColumns.Add(c);
	}
	for (int32 i = StartColumns.Num() - 1; i > 0; --i)
	{
		StartColumns.Swap(i, FMath::RandRange(0, i));
	}

	for (int32 Path = 0; Path < FMath::Max(1, Settings->Paths); ++Path)
	{
		int32 Column = StartColumns[Path % StartColumns.Num()];
		int32 Prev = 0;
		for (int32 Row = 1; Row <= Rows; ++Row)
		{
			const int32 Index = GetOrAdd(Row, Column);
			Nodes[Prev].Next.AddUnique(Index);
			Prev = Index;

			if (Row == Rows)
			{
				break;
			}
			int32 NextColumn = FMath::Clamp(Column + FMath::RandRange(-1, 1), 0, Columns - 1);
			// 이미 그어진 선과 X자로 엇갈리면 곧장 위로 간다.
			if (NextColumn != Column)
			{
				const int32* Side = Grid.Find(FIntPoint(Row, NextColumn));
				const int32* Above = Grid.Find(FIntPoint(Row + 1, Column));
				if (Side && Above && Nodes[*Side].Next.Contains(*Above))
				{
					NextColumn = Column;
				}
			}
			Column = NextColumn;
		}
	}

	// 줄 순서대로 방을 정한다. 바로 아래 칸들(부모)과 같은 방은 되도록 피한다.
	for (int32 Row = 1; Row <= Rows; ++Row)
	{
		for (int32 i = 1; i < Nodes.Num(); ++i)
		{
			if (Nodes[i].Row != Row)
			{
				continue;
			}
			TArray<int32> Candidates;
			for (int32 Room = 0; Room < RoomCount; ++Room)
			{
				bool bUsedByParent = false;
				for (const FRunMapNode& Parent : Nodes)
				{
					if (Parent.Next.Contains(i) && Parent.RoomIndex == Room)
					{
						bUsedByParent = true;
						break;
					}
				}
				if (!bUsedByParent)
				{
					Candidates.Add(Room);
				}
			}
			if (Candidates.Num() == 0)
			{
				for (int32 Room = 0; Room < RoomCount; ++Room)
				{
					Candidates.Add(Room);
				}
			}
			Nodes[i].RoomIndex = Candidates.Num() > 0 ? Candidates[FMath::RandRange(0, Candidates.Num() - 1)] : 0;
		}
	}
}

bool URunSubsystem::IsReachable(int32 NodeIndex) const
{
	return Nodes.IsValidIndex(CurrentNode) && Nodes[CurrentNode].Next.Contains(NodeIndex);
}

void URunSubsystem::OnExitDoorReached(APlayerController* PC)
{
	EnsureRun();
	if (!Nodes.IsValidIndex(CurrentNode) || Nodes[CurrentNode].Next.Num() == 0)
	{
		// 맨 위 칸까지 왔다. 아직 보스·끝 처리가 없어서 새 지도로 처음 방부터 다시 시작한다.
		Nodes.Reset();
		Generate();
		OpenRoomLevel(Nodes[CurrentNode].RoomIndex);
		return;
	}
	OpenMap(PC);
}

void URunSubsystem::OpenMap(APlayerController* PC)
{
	if (MapWidget || !PC)
	{
		return;
	}
	EnsureRun();

	MapWidget = CreateWidget<URoomMapWidget>(PC, URoomMapWidget::StaticClass());
	MapWidget->Init(this);
	MapWidget->AddToViewport(20);
	MapOwner = PC;

	PC->SetPause(true);
	PC->SetShowMouseCursor(true);
	FInputModeUIOnly Mode;
	Mode.SetWidgetToFocus(MapWidget->TakeWidget());
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	PC->SetInputMode(Mode);
}

void URunSubsystem::CloseMap()
{
	if (MapWidget)
	{
		MapWidget->RemoveFromParent();
		MapWidget = nullptr;
	}
	if (APlayerController* PC = MapOwner.Get())
	{
		PC->SetPause(false);
		PC->SetShowMouseCursor(false);
		PC->SetInputMode(FInputModeGameOnly());
	}
	MapOwner = nullptr;
}

void URunSubsystem::TravelTo(int32 NodeIndex)
{
	if (!IsReachable(NodeIndex))
	{
		return;
	}
	Nodes[CurrentNode].bVisited = true;
	CurrentNode = NodeIndex;
	CloseMap();
	OpenRoomLevel(Nodes[CurrentNode].RoomIndex);
}

void URunSubsystem::OpenRoomLevel(int32 RoomIndex)
{
	const URunSettings* Settings = GetDefault<URunSettings>();
	if (!Settings->Rooms.IsValidIndex(RoomIndex))
	{
		return;
	}
	UGameplayStatics::OpenLevelBySoftObjectPtr(GetGameInstance(), Settings->Rooms[RoomIndex].Level);
}

bool URoomWorldSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

void URoomWorldSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
	Super::OnWorldBeginPlay(InWorld);

	if (UGameInstance* GI = InWorld.GetGameInstance())
	{
		if (URunSubsystem* Run = GI->GetSubsystem<URunSubsystem>())
		{
			Run->EnsureRun();
		}
	}

	// 방마다 문 액터를 따로 놓지 않도록, 출구 문 메시가 있는 곳에 판정을 자동으로 붙인다.
	TArray<FTransform> Doors;
	for (TActorIterator<AStaticMeshActor> It(&InWorld); It; ++It)
	{
		const UStaticMesh* Mesh = It->GetStaticMeshComponent() ? It->GetStaticMeshComponent()->GetStaticMesh() : nullptr;
		if (Mesh && Mesh->GetName().EndsWith(TEXT("_ExitDoor")))
		{
			FTransform Transform = It->GetActorTransform();
			Transform.SetScale3D(FVector::OneVector);
			Doors.Add(Transform);
		}
	}
	for (const FTransform& Transform : Doors)
	{
		InWorld.SpawnActor<ARoomExitDoor>(ARoomExitDoor::StaticClass(), Transform);
	}
}
