#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "RunSettings.generated.h"

class UTexture2D;
class UFontFace;
class UWorld;

/** 지도에 놓일 수 있는 방 하나 */
USTRUCT(BlueprintType)
struct FRunRoom
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Config, Category = "Room")
	TSoftObjectPtr<UWorld> Level;

	/** 지도 칸 아래에 쓰는 이름 */
	UPROPERTY(EditAnywhere, Config, Category = "Room")
	FText DisplayName;
};

/**
 * 방 지도(런) 설정. 프로젝트 세팅 > Game > Run Map 에서 고친다(DefaultGame.ini에 저장).
 * 방 목록, 지도 크기, 지도 그림·배치 수치.
 */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Run Map"))
class PROJECTR_API URunSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	URunSettings();

	virtual FName GetCategoryName() const override { return TEXT("Game"); }

	/** 지도 칸에 배정할 방들. 이웃한 칸(부모)과 같은 방은 되도록 피한다. */
	UPROPERTY(EditAnywhere, Config, Category = "Rooms")
	TArray<FRunRoom> Rooms;

	/** 시작 칸의 방(Rooms 안의 순번) */
	UPROPERTY(EditAnywhere, Config, Category = "Rooms")
	int32 StartRoomIndex = 0;

	/** 시작 칸을 뺀 줄 수(아래에서 위로) */
	UPROPERTY(EditAnywhere, Config, Category = "Map", meta = (ClampMin = "1"))
	int32 Rows = 6;

	/** 한 줄에 놓일 수 있는 칸 자리 수 */
	UPROPERTY(EditAnywhere, Config, Category = "Map", meta = (ClampMin = "1"))
	int32 Columns = 5;

	/** 시작 칸에서 위로 뻗는 길 수(겹치면 합쳐진다) */
	UPROPERTY(EditAnywhere, Config, Category = "Map", meta = (ClampMin = "1"))
	int32 Paths = 3;

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	TSoftObjectPtr<UTexture2D> Backdrop;

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	TSoftObjectPtr<UTexture2D> NodeRoom;

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	TSoftObjectPtr<UTexture2D> NodeStart;

	/** 지금 있는 칸 */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	TSoftObjectPtr<UTexture2D> NodeCurrent;

	/** 지나온 칸 위에 긋는 X */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	TSoftObjectPtr<UTexture2D> VisitedMark;

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	TSoftObjectPtr<UFontFace> Font;

	/** 배경 그림 안에서 칸이 놓이는 영역(그림 크기 대비 0~1: 왼쪽, 위, 오른쪽, 아래) */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	FVector4 NodeArea = FVector4(0.2, 0.16, 0.8, 0.86);

	/** 지도 판 크기(화면 맞춤 전 기준 픽셀) */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	FVector2D BoardSize = FVector2D(1600.0, 893.0);

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	float NodeSize = 64.f;

	/** 갈 수 있는 칸이 숨쉬듯 커졌다 작아지는 정도(0.1 = 10%)와 속도(초당 회) */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	float PulseScale = 0.12f;

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	float PulseSpeed = 1.2f;

	/** 점선 한 칸 길이·빈칸·두께 */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	FVector DashLengthGapThickness = FVector(10.0, 8.0, 3.0);

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	FLinearColor InkColor = FLinearColor(0.16f, 0.09f, 0.04f, 0.85f);

	/** 갈 수 없는 칸의 불투명도 */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	float LockedOpacity = 0.55f;

	/** "Esc: 닫기" 글 위치(판 크기 대비 0~1). 맨 아래 가운데는 시작 칸 이름과 겹쳐서 왼쪽으로 뺐다. */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	FVector2D CloseHintPosition = FVector2D(0.32, 0.9);

	/** 지도 뒤를 덮는 색(불투명). 화면 비율이 그림과 달라 남는 곳에 보인다. */
	UPROPERTY(EditAnywhere, Config, Category = "Look")
	FLinearColor CoverColor = FLinearColor(1.f, 1.f, 1.f, 1.f);

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	int32 LabelFontSize = 20;

	UPROPERTY(EditAnywhere, Config, Category = "Look")
	int32 TitleFontSize = 34;
};
