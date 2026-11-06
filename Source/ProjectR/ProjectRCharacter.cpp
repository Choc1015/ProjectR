#include "ProjectRCharacter.h"

#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "Kismet/GameplayStatics.h"
#include "Rendering/SkeletalMeshRenderData.h"
#include "SkillTreeComponent.h"
#include "PlayerStatsComponent.h"
#include "PlayerHUDWidget.h"
#include "PlayerSkillComponent.h"
#include "SkillTreeWidget.h"
#include "TimerManager.h"
#include "Engine/DataTable.h"
#include "Engine/StaticMesh.h"
#include "ProjectRProjectile.h"
#include "RunSubsystem.h"
#include "WeaponPickup.h"
#include "InventoryComponent.h"
#include "InventoryWidget.h"
#include "WeaponTypes.h"

AProjectRCharacter::AProjectRCharacter()
{
	// 공격 카메라 전진을 처리한다. 애니메이션이 본 위치를 갱신한 뒤에 돈다.
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PostUpdateWork;

	GetCapsuleComponent()->InitCapsuleSize(35.f, 90.f);

	bUseControllerRotationYaw = true;
	GetCharacterMovement()->MaxWalkSpeed = 450.f;
	GetCharacterMovement()->bOrientRotationToMovement = false;

	// 눈 카메라: 캡슐에 붙고 마우스 시점(좌우·위아래)으로 돈다. 위치는 BP에서 눈 높이로 맞춘다.
	FirstPersonCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
	FirstPersonCamera->SetupAttachment(GetCapsuleComponent());
	FirstPersonCamera->SetRelativeLocation(FVector(0.f, 0.f, 70.f));
	FirstPersonCamera->bUsePawnControlRotation = true;
	FirstPersonCamera->SetFieldOfView(90.f);

	// 메시 원점은 발바닥, 미사모 임포트 결과 정면이 -X라 180도 돌린다. 캡슐 기준 위치·회전은 BP에서 맞춘다.
	GetMesh()->SetRelativeLocationAndRotation(FVector(0.f, 0.f, -90.f), FRotator(0.f, 180.f, 0.f));

	SkillTree = CreateDefaultSubobject<USkillTreeComponent>(TEXT("SkillTree"));
	Stats = CreateDefaultSubobject<UPlayerStatsComponent>(TEXT("Stats"));
	Skills = CreateDefaultSubobject<UPlayerSkillComponent>(TEXT("Skills"));
	Inventory = CreateDefaultSubobject<UInventoryComponent>(TEXT("Inventory"));
	SwordMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SwordMesh"));
	SwordMesh->SetupAttachment(GetMesh(), WeaponSocketName);
	SwordMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	// 미사모 손 본에는 x100 스케일이 들어 있어 상속하면 검이 거대해진다.
	SwordMesh->SetUsingAbsoluteScale(true);
}

void AProjectRCharacter::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);

	// 블루프린트에서 소켓 이름을 바꿨을 수 있으니 다시 붙인다. 위치·회전은 BP 값 그대로.
	SwordMesh->AttachToComponent(GetMesh(), FAttachmentTransformRules::KeepRelativeTransform, WeaponSocketName);
}

void AProjectRCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	UpdateAttackCameraPush(DeltaSeconds);
}

void AProjectRCharacter::UpdateAttackCameraPush(float DeltaSeconds)
{
	// 0 → 1 → 0 로 부드럽게: 나갔다가 원래 자리로 돌아온다.
	float PushAlpha = 0.f;
	if (AttackPushElapsed < AttackCameraPushTime)
	{
		AttackPushElapsed += DeltaSeconds;
		PushAlpha = FMath::Sin(UE_PI * FMath::Clamp(AttackPushElapsed / AttackCameraPushTime, 0.f, 1.f));
	}

	// 카메라 기준 고정 오프셋 + 공격 전진을 매 프레임 새로 건다(카메라 Transform 자체는 건드리지 않는다).
	FirstPersonCamera->ClearAdditiveOffset();
	const FVector Offset = CameraViewOffset + FVector(AttackCameraPushDistance * PushAlpha, 0.f, 0.f);
	if (!Offset.IsNearlyZero())
	{
		FirstPersonCamera->AddAdditiveOffset(FTransform(Offset), 0.f);
	}
}

void AProjectRCharacter::ApplyFirstPersonVisibility()
{
	USkeletalMeshComponent* BodyMesh = GetMesh();
	USkeletalMesh* MeshAsset = BodyMesh->GetSkeletalMeshAsset();
	if (!MeshAsset)
	{
		return;
	}

	for (const FName& BoneName : BodyHiddenBoneNames)
	{
		if (BodyMesh->GetBoneIndex(BoneName) != INDEX_NONE)
		{
			BodyMesh->HideBoneByName(BoneName, PBO_None);
		}
	}

	const FSkeletalMeshRenderData* RenderData = MeshAsset->GetResourceForRendering();
	if (!RenderData)
	{
		return;
	}
	for (int32 LODIndex = 0; LODIndex < RenderData->LODRenderData.Num(); ++LODIndex)
	{
		BodyMesh->ShowAllMaterialSections(LODIndex);
		const TArray<FSkelMeshRenderSection>& Sections = RenderData->LODRenderData[LODIndex].RenderSections;
		for (int32 SectionIndex = 0; SectionIndex < Sections.Num(); ++SectionIndex)
		{
			const int32 MaterialIndex = Sections[SectionIndex].MaterialIndex;
			const TArray<FSkeletalMaterial>& Materials = MeshAsset->GetMaterials();
			if (Materials.IsValidIndex(MaterialIndex) && BodyHiddenMaterialSlotNames.Contains(Materials[MaterialIndex].MaterialSlotName))
			{
				BodyMesh->ShowMaterialSection(MaterialIndex, SectionIndex, false, LODIndex);
			}
		}
	}
}

void AProjectRCharacter::BeginPlay()
{
	Super::BeginPlay();

	ApplyFirstPersonVisibility();
	SwordBaseRotation = SwordMesh->GetRelativeRotation().Quaternion();
	WeaponBaseTransform = SwordMesh->GetRelativeTransform();
	DefaultWeaponMesh = SwordMesh->GetStaticMesh();
	ActiveAttackMontages = AttackMontages;

	if (UAnimInstance* AnimInstance = GetMesh()->GetAnimInstance())
	{
		AnimInstance->OnPlayMontageNotifyBegin.AddDynamic(this, &AProjectRCharacter::OnMontageNotifyBegin);
	}

	if (const APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
			ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			Subsystem->AddMappingContext(DefaultMappingContext, 0);
		}
	}

	if (APlayerController* PC = Cast<APlayerController>(GetController()); PC && IsLocallyControlled())
	{
		HUDWidget = CreateWidget<UPlayerHUDWidget>(PC, UPlayerHUDWidget::StaticClass());
		HUDWidget->Init(Stats, HUDStyle);
		HUDWidget->AddToViewport(0);
	}

	// 방을 옮겨 새로 태어나도 런에서 들고 있던 무기를 다시 든다.
	FName StartWeapon = DefaultWeapon;
	if (const URunSubsystem* Run = GetGameInstance() ? GetGameInstance()->GetSubsystem<URunSubsystem>() : nullptr; Run && !Run->CurrentWeapon.IsNone())
	{
		StartWeapon = Run->CurrentWeapon;
	}
	EquipWeapon(StartWeapon);
}

const FWeaponRow* AProjectRCharacter::FindWeaponRow(FName WeaponId) const
{
	const UDataTable* Table = WeaponTable.LoadSynchronous();
	return Table && !WeaponId.IsNone() ? Table->FindRow<FWeaponRow>(WeaponId, TEXT("EquipWeapon")) : nullptr;
}

void AProjectRCharacter::EquipWeapon(FName WeaponId)
{
	const FWeaponRow* Row = FindWeaponRow(WeaponId);
	if (!Row)
	{
		return;
	}
	ResetCombo();
	CurrentWeapon = WeaponId;

	// 손 메시: BP에서 맞춘 손잡이 위치 위에 무기별 오프셋을 더한다.
	// 손 본에 x100 스케일이 있어 상대 위치는 그만큼 나눠야 cm 단위가 된다(스케일은 절대값이라 그대로).
	UStaticMesh* HeldMesh = Row->Mesh.IsNull() ? DefaultWeaponMesh.Get() : Row->Mesh.LoadSynchronous();
	SwordMesh->SetStaticMesh(HeldMesh);
	const FQuat BaseRotation = WeaponBaseTransform.GetRotation();
	const double ParentScale = FMath::Max(KINDA_SMALL_NUMBER, SwordMesh->GetAttachParent()
		? SwordMesh->GetAttachParent()->GetSocketTransform(SwordMesh->GetAttachSocketName()).GetScale3D().X : 1.0);
	SwordBaseRotation = BaseRotation * Row->MeshOffsetRotation.Quaternion();
	SwordMesh->SetRelativeLocationAndRotation(
		WeaponBaseTransform.GetLocation() + BaseRotation.RotateVector(Row->MeshOffsetLocation) / ParentScale,
		SwordBaseRotation);
	SwordMesh->SetRelativeScale3D(WeaponBaseTransform.GetScale3D() * Row->MeshScale);

	// 공격 몽타주: 표에 없으면 BP의 검 콤보(공격별 검 회전 포함)
	ActiveAttackMontages.Reset();
	bUseSwordComboRotations = Row->AttackMontages.IsEmpty();
	if (bUseSwordComboRotations)
	{
		ActiveAttackMontages = AttackMontages;
	}
	else
	{
		for (const TSoftObjectPtr<UAnimMontage>& Montage : Row->AttackMontages)
		{
			if (UAnimMontage* Loaded = Montage.LoadSynchronous())
			{
				ActiveAttackMontages.Add(Loaded);
			}
		}
	}

	if (!Row->WeaponSkill.IsNone())
	{
		Skills->WeaponSkill = Row->WeaponSkill;
	}

	if (URunSubsystem* Run = GetGameInstance() ? GetGameInstance()->GetSubsystem<URunSubsystem>() : nullptr)
	{
		Run->CurrentWeapon = WeaponId;
	}
}

void AProjectRCharacter::SetNearbyPickup(AWeaponPickup* Pickup)
{
	NearbyPickup = Pickup;
	const FWeaponRow* Row = Pickup ? Pickup->FindRow() : nullptr;
	if (HUDWidget && Row)
	{
		HUDWidget->SetPrompt(FText::Format(FText::FromString(TEXT("E   {0} 줍기")), Row->DisplayName));
	}
}

void AProjectRCharacter::ClearNearbyPickup(AWeaponPickup* Pickup)
{
	if (NearbyPickup.Get() == Pickup)
	{
		NearbyPickup = nullptr;
		if (HUDWidget)
		{
			HUDWidget->SetPrompt(FText::GetEmpty());
		}
	}
}

void AProjectRCharacter::PickUpNearbyWeapon()
{
	// 주운 무기는 가방으로 들어간다(가방이 가득 차면 줍지 않는다). 바꿔 들기는 인벤토리에서.
	AWeaponPickup* Pickup = NearbyPickup.Get();
	if (!Pickup || !Inventory->AddItem(Pickup->WeaponId))
	{
		return;
	}
	ClearNearbyPickup(Pickup);
	Pickup->SetWeapon(NAME_None);
}

void AProjectRCharacter::FireWeaponProjectile(const FWeaponRow& Row)
{
	// 화면 가운데가 겨눈 곳: 카메라에서 앞으로 쏜 선이 닿는 점을 향해 무기 끝에서 쏜다.
	const FVector CameraLocation = FirstPersonCamera->GetComponentLocation();
	const FVector Forward = FirstPersonCamera->GetForwardVector();
	FVector Target = CameraLocation + Forward * 5000.f;
	FHitResult AimHit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(ProjectRAim), false, this);
	if (GetWorld()->LineTraceSingleByChannel(AimHit, CameraLocation + Forward * 50.f, Target, ECC_Visibility, Params))
	{
		Target = AimHit.ImpactPoint;
	}

	FVector Muzzle = SwordMesh->GetComponentTransform().TransformPosition(Row.ProjectileMuzzle);
	// 무기 끝이 카메라 뒤에 있으면 벽 안에서 나올 수 있어 카메라 앞으로 당긴다.
	if (FVector::DotProduct(Muzzle - CameraLocation, Forward) < 30.f)
	{
		Muzzle = CameraLocation + Forward * 60.f;
	}

	bool bCrit = false;
	FProjectileLaunch Launch;
	Launch.Location = Muzzle;
	Launch.Direction = Target - Muzzle;
	Launch.Mesh = Row.ProjectileMesh.LoadSynchronous();
	Launch.Speed = Row.ProjectileSpeed;
	Launch.Damage = Stats->RollOutgoingDamage(false, bCrit) * Row.ProjectileDamageMultiplier;
	AProjectRProjectile::Launch(this, Launch);
}

void AProjectRCharacter::CreateInput()
{
	if (DefaultMappingContext)
	{
		return;
	}

	MoveAction = NewObject<UInputAction>(this, TEXT("IA_Move"));
	MoveAction->ValueType = EInputActionValueType::Axis2D;
	LookAction = NewObject<UInputAction>(this, TEXT("IA_Look"));
	LookAction->ValueType = EInputActionValueType::Axis2D;
	JumpAction = NewObject<UInputAction>(this, TEXT("IA_Jump"));
	AttackAction = NewObject<UInputAction>(this, TEXT("IA_Attack"));
	SkillTreeAction = NewObject<UInputAction>(this, TEXT("IA_SkillTree"));
	InventoryAction = NewObject<UInputAction>(this, TEXT("IA_Inventory"));

	DefaultMappingContext = NewObject<UInputMappingContext>(this, TEXT("IMC_Default"));

	// Move: X = 오른쪽, Y = 앞쪽
	auto MapMoveKey = [this](FKey Key, bool bSwizzle, bool bNegate)
	{
		FEnhancedActionKeyMapping& Mapping = DefaultMappingContext->MapKey(MoveAction, Key);
		if (bSwizzle)
		{
			Mapping.Modifiers.Add(NewObject<UInputModifierSwizzleAxis>(DefaultMappingContext));
		}
		if (bNegate)
		{
			Mapping.Modifiers.Add(NewObject<UInputModifierNegate>(DefaultMappingContext));
		}
	};
	MapMoveKey(EKeys::W, true, false);
	MapMoveKey(EKeys::S, true, true);
	MapMoveKey(EKeys::D, false, false);
	MapMoveKey(EKeys::A, false, true);

	FEnhancedActionKeyMapping& LookMapping = DefaultMappingContext->MapKey(LookAction, EKeys::Mouse2D);
	UInputModifierNegate* InvertY = NewObject<UInputModifierNegate>(DefaultMappingContext);
	InvertY->bX = false;
	InvertY->bZ = false;
	LookMapping.Modifiers.Add(InvertY);

	DefaultMappingContext->MapKey(JumpAction, EKeys::SpaceBar);
	DefaultMappingContext->MapKey(AttackAction, EKeys::LeftMouseButton);
	DefaultMappingContext->MapKey(SkillTreeAction, EKeys::K);
	DefaultMappingContext->MapKey(InventoryAction, EKeys::I);

	const FKey SkillKeys[] = { EKeys::Q, EKeys::E, EKeys::R, EKeys::F };
	for (int32 Slot = 0; Slot < UE_ARRAY_COUNT(SkillKeys); ++Slot)
	{
		UInputAction* Action = NewObject<UInputAction>(this, *FString::Printf(TEXT("IA_SkillSlot%d"), Slot));
		SkillSlotActions.Add(Action);
		DefaultMappingContext->MapKey(Action, SkillKeys[Slot]);
	}
}

void AProjectRCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	CreateInput();

	if (UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		Input->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AProjectRCharacter::Move);
		Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &AProjectRCharacter::Look);
		Input->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
		Input->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
		Input->BindAction(AttackAction, ETriggerEvent::Started, this, &AProjectRCharacter::Attack);
		Input->BindAction(SkillTreeAction, ETriggerEvent::Started, this, &AProjectRCharacter::ToggleSkillTree);
		Input->BindAction(InventoryAction, ETriggerEvent::Started, this, &AProjectRCharacter::ToggleInventory);
		for (int32 Slot = 0; Slot < SkillSlotActions.Num(); ++Slot)
		{
			Input->BindAction(SkillSlotActions[Slot], ETriggerEvent::Started, this, &AProjectRCharacter::UseSkillSlot, Slot);
		}
	}
}

void AProjectRCharacter::Move(const FInputActionValue& Value)
{
	if (SkillTreeWidget)
	{
		return;
	}
	const FVector2D Axis = Value.Get<FVector2D>();
	const FRotator YawRotation(0.f, GetControlRotation().Yaw, 0.f);
	AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Axis.X);
}

void AProjectRCharacter::Look(const FInputActionValue& Value)
{
	if (SkillTreeWidget)
	{
		return;
	}
	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X);
	AddControllerPitchInput(Axis.Y);
}

void AProjectRCharacter::Attack()
{
	if (SkillTreeWidget || ActiveAttackMontages.IsEmpty() || Skills->IsBusy())
	{
		return;
	}

	if (ComboIndex == INDEX_NONE)
	{
		PlayComboAttack(0);
	}
	else
	{
		bComboQueued = true;
	}
}

void AProjectRCharacter::PlayComboAttack(int32 Index)
{
	UAnimMontage* Montage = ActiveAttackMontages[Index];
	UAnimInstance* AnimInstance = GetMesh()->GetAnimInstance();
	if (!Montage || !AnimInstance)
	{
		ResetCombo();
		return;
	}

	ComboIndex = Index;
	bComboQueued = false;

	// 공격 속도 스탯(100 = 원래 속도)만큼 빨리 재생한다. Duration도 빨라진 길이라 판정·콤보 타이밍이 같이 당겨진다.
	const float PlayRate = FMath::Max(0.1f, Stats->GetStat(EPlayerStat::AttackSpeed) / 100.f);
	const float Duration = AnimInstance->Montage_Play(Montage, PlayRate, EMontagePlayReturnType::Duration);
	if (Duration <= 0.f)
	{
		ResetCombo();
		return;
	}

	// 타마다 카메라를 앞으로 살짝 내밀었다가 되돌린다.
	AttackPushElapsed = 0.f;

	// 이 타에서 칼날이 맞는 면을 향하도록 검을 돌린다.
	const FRotator SwordOffset = bUseSwordComboRotations && AttackSwordRotationOffsets.IsValidIndex(Index) ? AttackSwordRotationOffsets[Index] : FRotator::ZeroRotator;
	SwordMesh->SetRelativeRotation(SwordBaseRotation * SwordOffset.Quaternion());

	FOnMontageEnded EndDelegate;
	EndDelegate.BindUObject(this, &AProjectRCharacter::OnAttackMontageEnded);
	AnimInstance->Montage_SetEndDelegate(EndDelegate, Montage);

	FTimerManager& Timers = GetWorldTimerManager();
	// Hit 노티파이가 있으면 그 프레임에서 판정하고, 없으면 몽타주 길이 비율로 판정한다.
	if (!HasHitNotify(Montage))
	{
		Timers.SetTimer(HitTimer, this, &AProjectRCharacter::PerformHitTrace, Duration * HitTimeFraction, false);
	}
	Timers.SetTimer(ComboTimer, this, &AProjectRCharacter::OnComboTime, Duration * ComboTimeFraction, false);
}

bool AProjectRCharacter::HasHitNotify(const UAnimMontage* Montage) const
{
	const FString HitName = HitNotifyName.ToString();
	return Montage->Notifies.ContainsByPredicate([&HitName](const FAnimNotifyEvent& Event)
	{
		return Event.Notify && Event.Notify->GetNotifyName() == HitName;
	});
}

void AProjectRCharacter::OnMontageNotifyBegin(FName NotifyName, const FBranchingPointNotifyPayload& Payload)
{
	if (NotifyName == HitNotifyName && ComboIndex != INDEX_NONE)
	{
		PerformHitTrace();
	}
}

void AProjectRCharacter::PerformHitTrace()
{
	if (const FWeaponRow* Row = FindWeaponRow(CurrentWeapon); Row && Row->bProjectileAttack)
	{
		FireWeaponProjectile(*Row);
		return;
	}

	const UCameraComponent* Camera = FirstPersonCamera;
	const FVector Start = Camera->GetComponentLocation();
	const FVector End = Start + Camera->GetForwardVector() * AttackRange;

	FCollisionQueryParams Params(SCENE_QUERY_STAT(ProjectRAttack), false, this);
	TArray<FHitResult> Hits;
	GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Visibility,
		FCollisionShape::MakeSphere(AttackRadius), Params);

	TSet<AActor*> Damaged;
	for (const FHitResult& Hit : Hits)
	{
		AActor* HitActor = Hit.GetActor();
		if (HitActor && !Damaged.Contains(HitActor))
		{
			Damaged.Add(HitActor);
			bool bCrit = false;
			const float Damage = Stats->RollOutgoingDamage(false, bCrit);
			UGameplayStatics::ApplyPointDamage(HitActor, Damage, GetActorForwardVector(), Hit,
				GetController(), this, nullptr);
		}
	}
}

float AProjectRCharacter::TakeDamage(float DamageAmount, const FDamageEvent& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
	const float Raw = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
	const UPlayerStatsComponent* AttackerStats = DamageCauser ? DamageCauser->FindComponentByClass<UPlayerStatsComponent>() : nullptr;
	return Stats->ApplyIncomingDamage(Raw, AttackerStats ? AttackerStats->GetStat(EPlayerStat::ArmorPenetration) : 0.f);
}

void AProjectRCharacter::OnComboTime()
{
	if (bComboQueued && ActiveAttackMontages.IsValidIndex(ComboIndex + 1))
	{
		PlayComboAttack(ComboIndex + 1);
	}
}

void AProjectRCharacter::OnAttackMontageEnded(UAnimMontage* Montage, bool bInterrupted)
{
	// 다음 타로 넘어가며 끊긴 경우는 콤보가 이어지는 중이다.
	if (ActiveAttackMontages.IsValidIndex(ComboIndex) && Montage == ActiveAttackMontages[ComboIndex])
	{
		ResetCombo();
	}
}

void AProjectRCharacter::ResetCombo()
{
	ComboIndex = INDEX_NONE;
	bComboQueued = false;
	SwordMesh->SetRelativeRotation(SwordBaseRotation);
	GetWorldTimerManager().ClearTimer(HitTimer);
	GetWorldTimerManager().ClearTimer(ComboTimer);
}

void AProjectRCharacter::UseSkillSlot(int32 Slot)
{
	if (SkillTreeWidget)
	{
		return;
	}
	// 바닥 무기 근처에서는 E(젬 두 번째 칸)가 줍기다.
	if (Slot == 1 && NearbyPickup.IsValid())
	{
		PickUpNearbyWeapon();
		return;
	}
	// 기본 공격 중이면 콤보를 끊고 스킬을 쓴다(몽타주가 바뀌며 콤보 정리는 끝 이벤트가 한다).
	if (Skills->TryUseSlot(Slot))
	{
		ResetCombo();
	}
}

void AProjectRCharacter::ToggleInventory()
{
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC)
	{
		return;
	}

	if (InventoryWidget)
	{
		InventoryWidget->RemoveFromParent();
		InventoryWidget = nullptr;
		PC->SetPause(false);
		PC->SetShowMouseCursor(false);
		PC->SetInputMode(FInputModeGameOnly());
		return;
	}
	if (SkillTreeWidget)
	{
		return;
	}

	InventoryWidget = CreateWidget<UInventoryWidget>(PC, UInventoryWidget::StaticClass());
	InventoryWidget->Init(this, Inventory);
	InventoryWidget->AddToViewport(15);
	PC->SetPause(true);
	PC->SetShowMouseCursor(true);
	FInputModeUIOnly Mode;
	Mode.SetWidgetToFocus(InventoryWidget->TakeWidget());
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	PC->SetInputMode(Mode);
}

void AProjectRCharacter::ToggleSkillTree()
{
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC)
	{
		return;
	}

	if (SkillTreeWidget)
	{
		SkillTreeWidget->RemoveFromParent();
		SkillTreeWidget = nullptr;
		PC->SetShowMouseCursor(false);
		PC->SetInputMode(FInputModeGameOnly());
		return;
	}

	// 열 때마다 새로 만들어 표에 추가된 스킬이 바로 배치되게 한다.
	SkillTreeWidget = CreateWidget<USkillTreeWidget>(PC, USkillTreeWidget::StaticClass());
	SkillTreeWidget->Init(SkillTree);
	SkillTreeWidget->AddToViewport(10);
	PC->SetShowMouseCursor(true);
	FInputModeGameAndUI Mode;
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	Mode.SetHideCursorDuringCapture(false);
	PC->SetInputMode(Mode);
}
