#include "RunSettings.h"

#include "Engine/FontFace.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"

URunSettings::URunSettings()
{
	FRunRoom Temple;
	Temple.Level = TSoftObjectPtr<UWorld>(FSoftObjectPath(TEXT("/Game/Maps/Rooms/L_Room_ForestTemple.L_Room_ForestTemple")));
	Temple.DisplayName = FText::FromString(TEXT("숲속 신전"));
	Rooms.Add(Temple);

	FRunRoom Mine;
	Mine.Level = TSoftObjectPtr<UWorld>(FSoftObjectPath(TEXT("/Game/Maps/Rooms/L_Room_Mine.L_Room_Mine")));
	Mine.DisplayName = FText::FromString(TEXT("버려진 광산"));
	Rooms.Add(Mine);

	Backdrop = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Map/T_MapBackdrop.T_MapBackdrop")));
	NodeRoom = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Map/T_MapNode_Combat.T_MapNode_Combat")));
	NodeStart = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Map/T_MapNode_Start.T_MapNode_Start")));
	NodeCurrent = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Map/T_MapNode_Current.T_MapNode_Current")));
	VisitedMark = TSoftObjectPtr<UTexture2D>(FSoftObjectPath(TEXT("/Game/UI/Map/T_MapCross.T_MapCross")));
	Font = TSoftObjectPtr<UFontFace>(FSoftObjectPath(TEXT("/Game/UI/Fonts/FF_NanumPenScript.FF_NanumPenScript")));
}
