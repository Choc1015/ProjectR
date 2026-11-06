#include "WeaponPickup.h"

#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/DataTable.h"
#include "Engine/StaticMesh.h"
#include "ProjectRCharacter.h"
#include "WeaponTypes.h"

AWeaponPickup::AWeaponPickup()
{
	PrimaryActorTick.bCanEverTick = true;

	Trigger = CreateDefaultSubobject<USphereComponent>(TEXT("Trigger"));
	Trigger->InitSphereRadius(140.f);
	Trigger->SetCollisionProfileName(TEXT("Trigger"));
	Trigger->OnComponentBeginOverlap.AddDynamic(this, &AWeaponPickup::HandleBeginOverlap);
	Trigger->OnComponentEndOverlap.AddDynamic(this, &AWeaponPickup::HandleEndOverlap);
	SetRootComponent(Trigger);

	Display = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Display"));
	Display->SetupAttachment(Trigger);
	Display->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	WeaponTable = TSoftObjectPtr<UDataTable>(FSoftObjectPath(TEXT("/Game/Data/DT_Weapons.DT_Weapons")));
}

const FWeaponRow* AWeaponPickup::FindRow() const
{
	const UDataTable* Table = WeaponTable.LoadSynchronous();
	return Table && !WeaponId.IsNone() ? Table->FindRow<FWeaponRow>(WeaponId, TEXT("WeaponPickup")) : nullptr;
}

void AWeaponPickup::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	RefreshDisplay();
}

void AWeaponPickup::RefreshDisplay()
{
	const FWeaponRow* Row = FindRow();
	Display->SetStaticMesh(Row ? Row->Mesh.LoadSynchronous() : nullptr);
	Display->SetRelativeLocation(FVector(0.f, 0.f, HoverHeight));
}

void AWeaponPickup::SetWeapon(FName NewWeaponId)
{
	WeaponId = NewWeaponId;
	if (WeaponId.IsNone() || !FindRow())
	{
		Destroy();
		return;
	}
	RefreshDisplay();
}

void AWeaponPickup::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	Time += DeltaSeconds;
	Display->SetRelativeLocationAndRotation(
		FVector(0.f, 0.f, HoverHeight + BobAmount * FMath::Sin(Time * 2.f)),
		FRotator(0.f, Time * SpinSpeed, 0.f));
}

void AWeaponPickup::HandleBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
	int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AProjectRCharacter* Character = Cast<AProjectRCharacter>(OtherActor))
	{
		Character->SetNearbyPickup(this);
	}
}

void AWeaponPickup::HandleEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (AProjectRCharacter* Character = Cast<AProjectRCharacter>(OtherActor))
	{
		Character->ClearNearbyPickup(this);
	}
}
