#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Subsystems/WorldSubsystem.h"
#include "RunSubsystem.generated.h"

class APlayerController;
class URoomMapWidget;

/** 지도 칸 하나. Row 0은 시작 칸, 위로 갈수록 Row가 커진다. */
USTRUCT()
struct FRunMapNode
{
	GENERATED_BODY()

	int32 Row = 0;
	int32 Column = 0;

	/** URunSettings::Rooms 안의 순번 */
	int32 RoomIndex = 0;

	/** 다음 줄에서 이어진 칸들(Nodes 순번) */
	TArray<int32> Next;

	/** 손으로 그린 느낌을 내려고 칸마다 조금씩 흔드는 위치(칸 간격 대비) */
	FVector2D Jitter = FVector2D::ZeroVector;

	bool bVisited = false;
};

/**
 * 한 판(런) 동안 유지되는 방 지도. 레벨을 옮겨도 남도록 게임 인스턴스에 붙는다.
 * 출구 문에 닿으면 지도를 열고, 고른 칸의 방 레벨로 이동한다.
 */
UCLASS()
class PROJECTR_API URunSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	/** 지도가 없으면 새로 만들고 시작 칸에 선다. */
	void EnsureRun();

	/** 출구 문에 닿았을 때. 다음 칸이 없으면(맨 위) 새 지도로 처음 방부터 다시 시작한다. */
	void OnExitDoorReached(APlayerController* PC);

	void OpenMap(APlayerController* PC);
	void CloseMap();
	bool IsMapOpen() const { return MapWidget != nullptr; }

	/** 지금 칸에서 이어진 칸이면 그 방으로 이동한다. */
	void TravelTo(int32 NodeIndex);

	const TArray<FRunMapNode>& GetNodes() const { return Nodes; }
	int32 GetCurrentNode() const { return CurrentNode; }
	bool IsReachable(int32 NodeIndex) const;

private:
	void Generate();
	void OpenRoomLevel(int32 RoomIndex);

	UPROPERTY(Transient)
	TArray<FRunMapNode> Nodes;

	int32 CurrentNode = INDEX_NONE;

	UPROPERTY(Transient)
	TObjectPtr<URoomMapWidget> MapWidget;

	TWeakObjectPtr<APlayerController> MapOwner;
};

/** 게임 월드가 시작될 때 런을 준비하고, 출구 문 메시(SM_*_ExitDoor)마다 출구 판정을 붙인다. */
UCLASS()
class PROJECTR_API URoomWorldSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual void OnWorldBeginPlay(UWorld& InWorld) override;

protected:
	virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;
};
