#include "RoomExitDoor.h"

#include "Components/BoxComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "RunSubsystem.h"

ARoomExitDoor::ARoomExitDoor()
{
	PrimaryActorTick.bCanEverTick = false;

	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);

	// 문 앞(방 쪽 +Y) 1m 안쪽, 문 폭 3m, 높이 5m
	Trigger = CreateDefaultSubobject<UBoxComponent>(TEXT("Trigger"));
	Trigger->SetupAttachment(Root);
	Trigger->SetRelativeLocation(FVector(0.f, 80.f, 250.f));
	Trigger->SetBoxExtent(FVector(150.f, 80.f, 250.f));
	Trigger->SetCollisionProfileName(TEXT("Trigger"));
	Trigger->OnComponentBeginOverlap.AddDynamic(this, &ARoomExitDoor::HandleOverlap);
}

void ARoomExitDoor::HandleOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	const APawn* Pawn = Cast<APawn>(OtherActor);
	APlayerController* PC = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	if (!PC || !PC->IsLocalController())
	{
		return;
	}
	if (URunSubsystem* Run = GetGameInstance() ? GetGameInstance()->GetSubsystem<URunSubsystem>() : nullptr)
	{
		Run->OnExitDoorReached(PC);
	}
}
