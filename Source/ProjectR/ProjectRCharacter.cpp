#include "ProjectRCharacter.h"

#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "AnimationRuntime.h"
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

AProjectRCharacter::AProjectRCharacter()
{
	// 카메라 회전·공격 전진을 처리한다. 애니메이션이 본 위치를 갱신한 뒤에 돈다.
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PostUpdateWork;

	GetCapsuleComponent()->InitCapsuleSize(35.f, 90.f);

	bUseControllerRotationYaw = true;
	GetCharacterMovement()->MaxWalkSpeed = 450.f;
	GetCharacterMovement()->bOrientRotationToMovement = false;

	FirstPersonCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
	FirstPersonCamera->SetupAttachment(GetCapsuleComponent());
	FirstPersonCamera->SetRelativeLocation(FVector(0.f, 0.f, 70.f));
	FirstPersonCamera->bUsePawnControlRotation = true;
	FirstPersonCamera->SetFieldOfView(90.f);

	// 몸 따라가기 모드의 카메라. 머리 본에 붙어 위치를 따라가고, 회전은 Tick이 정한다.
	// 위치는 BP 뷰포트에서 눈 위치로 끌어 맞춘다(미사모 본 스케일 때문에 숫자는 작게 보인다).
	HeadCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("HeadCamera"));
	HeadCamera->SetupAttachment(GetMesh(), CameraBoneName);
	HeadCamera->SetUsingAbsoluteRotation(true);
	HeadCamera->SetUsingAbsoluteScale(true);
	HeadCamera->bUsePawnControlRotation = false;
	HeadCamera->SetFieldOfView(90.f);

	// 메시 원점은 발바닥, 미사모 임포트 결과 정면이 -X라 180도 돌린다.
	// 팔 부착 모드에서는 ApplyCameraMode가 카메라에 다시 붙이며, 이 값은 그때 카메라 기준 위치가 된다.
	GetMesh()->SetRelativeLocationAndRotation(FVector(0.f, 0.f, -90.f), FRotator(0.f, 180.f, 0.f));
	GetMesh()->SetCastShadow(false);

	SkillTree = CreateDefaultSubobject<USkillTreeComponent>(TEXT("SkillTree"));
	Stats = CreateDefaultSubobject<UPlayerStatsComponent>(TEXT("Stats"));
	Skills = CreateDefaultSubobject<UPlayerSkillComponent>(TEXT("Skills"));
	SwordMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SwordMesh"));
	SwordMesh->SetupAttachment(GetMesh(), WeaponSocketName);
	SwordMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	// 미사모 손 본에는 x100 스케일이 들어 있어 상속하면 검이 거대해진다.
	SwordMesh->SetUsingAbsoluteScale(true);
}

void AProjectRCharacter::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);

	// 블루프린트에서 소켓 이름을 바꿨을 수 있으니 다시 붙인다. 에디터 배치 시에도 손에 보이게 여기서 한다.
	SwordMesh->AttachToComponent(GetMesh(), FAttachmentTransformRules::KeepRelativeTransform, WeaponSocketName);
	HeadCamera->AttachToComponent(GetMesh(), FAttachmentTransformRules::KeepRelativeTransform, CameraBoneName);

	ApplyCameraMode();
}

void AProjectRCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	UpdateHeadCameraRotation(DeltaSeconds);
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

	// 카메라 기준 고정 오프셋 + 공격 전진을 매 프레임 새로 건다.
	UCameraComponent* Camera = GetActiveCamera();
	Camera->ClearAdditiveOffset();
	const FVector Offset = CameraViewOffset + FVector(AttackCameraPushDistance * PushAlpha, 0.f, 0.f);
	if (!Offset.IsNearlyZero())
	{
		Camera->AddAdditiveOffset(FTransform(Offset), 0.f);
	}
}

void AProjectRCharacter::UpdateHeadCameraRotation(float DeltaSeconds)
{
	if (bUseHeadSocketRotation)
	{
		return;
	}

	USkeletalMeshComponent* BodyMesh = GetMesh();
	const int32 BoneIndex = BodyMesh->GetBoneIndex(CameraBoneName);
	if (CameraMode != EFirstPersonCameraMode::CameraFollowsBody || BoneIndex == INDEX_NONE
		|| !BodyMesh->GetComponentSpaceTransforms().IsValidIndex(BoneIndex))
	{
		return;
	}

	// 머리가 바라보는 방향(캡슐 공간). T포즈에서 머리가 정면(+X)을 본다고 보고, 그 대비 회전으로 구한다.
	const FQuat RefHead = FAnimationRuntime::GetComponentSpaceTransformRefPose(
		BodyMesh->GetSkeletalMeshAsset()->GetRefSkeleton(), BoneIndex).GetRotation();
	const FQuat AnimHead = BodyMesh->GetComponentSpaceTransforms()[BoneIndex].GetRotation();
	const FQuat MeshToActor = BodyMesh->GetRelativeRotation().Quaternion();
	const FQuat HeadDelta = MeshToActor * (AnimHead * RefHead.Inverse()) * MeshToActor.Inverse();
	// 롤은 버린다. 화면이 기울면 안 된다.
	const FRotator HeadDirection = HeadDelta.RotateVector(FVector::ForwardVector).Rotation();

	// 스탠스 때문에 대기 자세에서도 머리가 정면과 어긋나 있으니, 시작 직후 대기 자세 머리 방향을 기준(0)으로 삼는다.
	if (!bHasCameraBaseline)
	{
		CameraBaselineDelay -= DeltaSeconds;
		if (CameraBaselineDelay <= 0.f && ComboIndex == INDEX_NONE)
		{
			CameraBaseline = HeadDirection;
			bHasCameraBaseline = true;
		}
	}

	FRotator HeadOffset = FRotator::ZeroRotator;
	if (bHasCameraBaseline)
	{
		HeadOffset = (HeadDirection - CameraBaseline).GetNormalized() * CameraRotationFollowAlpha;
		HeadOffset.Roll = 0.f;
	}

	// 마우스 시점 위에 머리 움직임을 더한다.
	// 위치는 머리 본에 붙은 HeadCamera가 따라가므로 회전만 정한다.
	FRotator ViewRotation = GetControlRotation() + HeadOffset;
	ViewRotation.Pitch = FMath::ClampAngle(ViewRotation.Pitch, -89.f, 89.f);
	ViewRotation.Roll = 0.f;
	HeadCamera->SetWorldRotation(ViewRotation);
}

void AProjectRCharacter::AlignHeadCameraToSocket()
{
	HeadCamera->SetUsingAbsoluteRotation(!bUseHeadSocketRotation);
	if (!bUseHeadSocketRotation)
	{
		return;
	}

	USkeletalMeshComponent* BodyMesh = GetMesh();
	const USkeletalMesh* MeshAsset = BodyMesh->GetSkeletalMeshAsset();
	const int32 BoneIndex = MeshAsset ? MeshAsset->GetRefSkeleton().FindBoneIndex(CameraBoneName) : INDEX_NONE;
	if (BoneIndex == INDEX_NONE)
	{
		return;
	}

	// 기준 포즈에서 카메라가 캐릭터 정면(캡슐 +X)을 보고 위가 +Z가 되도록, 머리 본 기준 회전을 구한다.
	const FQuat RefHead = FAnimationRuntime::GetComponentSpaceTransformRefPose(MeshAsset->GetRefSkeleton(), BoneIndex).GetRotation();
	const FQuat ActorToMesh = BodyMesh->GetRelativeRotation().Quaternion().Inverse();
	const FQuat CameraInMesh = FRotationMatrix::MakeFromXZ(
		ActorToMesh.RotateVector(FVector::ForwardVector), ActorToMesh.RotateVector(FVector::UpVector)).ToQuat();
	HeadCamera->SetRelativeRotation(RefHead.Inverse() * CameraInMesh * HeadSocketRotationOffset.Quaternion());
}

UCameraComponent* AProjectRCharacter::GetActiveCamera() const
{
	return CameraMode == EFirstPersonCameraMode::CameraFollowsBody ? HeadCamera : FirstPersonCamera;
}

bool AProjectRCharacter::ShouldUseLocomotionAnimation() const
{
	return bPlayLocomotionAnimation;
}

void AProjectRCharacter::ApplyCameraMode()
{
	// 몸 전체가 보이는 모드에서만 그림자를 드리운다. 팔만 있을 때 그림자는 어색하다.
	GetMesh()->SetCastShadow(CameraMode == EFirstPersonCameraMode::CameraFollowsBody);
	// 뷰 타깃은 활성화된 첫 카메라를 쓰므로 모드에 맞는 카메라 하나만 켠다.
	FirstPersonCamera->SetActive(CameraMode == EFirstPersonCameraMode::ArmsOnCamera);
	HeadCamera->SetActive(CameraMode == EFirstPersonCameraMode::CameraFollowsBody);

	// 부모만 바꾼다. 위치·회전은 BP에서 CharacterMesh0에 정한 값을 그대로 쓴다.
	if (CameraMode == EFirstPersonCameraMode::CameraFollowsBody)
	{
		GetMesh()->AttachToComponent(GetCapsuleComponent(), FAttachmentTransformRules::KeepRelativeTransform);
		AlignHeadCameraToSocket();
		bHasCameraBaseline = false;
		CameraBaselineDelay = 0.3f;
		ApplyFirstPersonVisibility(BodyHiddenBoneNames, BodyHiddenMaterialSlotNames);
	}
	else
	{
		GetMesh()->AttachToComponent(FirstPersonCamera, FAttachmentTransformRules::KeepRelativeTransform);
		ApplyFirstPersonVisibility(HiddenBoneNames, HiddenMaterialSlotNames);
	}
}

void AProjectRCharacter::ApplyFirstPersonVisibility(const TArray<FName>& BoneNames, const TArray<FName>& MaterialSlotNames)
{
	USkeletalMeshComponent* BodyMesh = GetMesh();
	USkeletalMesh* MeshAsset = BodyMesh->GetSkeletalMeshAsset();
	if (!MeshAsset)
	{
		return;
	}

	for (const FName& BoneName : BoneNames)
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
			if (Materials.IsValidIndex(MaterialIndex) && MaterialSlotNames.Contains(Materials[MaterialIndex].MaterialSlotName))
			{
				BodyMesh->ShowMaterialSection(MaterialIndex, SectionIndex, false, LODIndex);
			}
		}
	}
}

void AProjectRCharacter::BeginPlay()
{
	Super::BeginPlay();

	ApplyCameraMode();
	SwordBaseRotation = SwordMesh->GetRelativeRotation().Quaternion();

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
	if (SkillTreeWidget || AttackMontages.IsEmpty() || Skills->IsBusy())
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
	UAnimMontage* Montage = AttackMontages[Index];
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
	const FRotator SwordOffset = AttackSwordRotationOffsets.IsValidIndex(Index) ? AttackSwordRotationOffsets[Index] : FRotator::ZeroRotator;
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
	const UCameraComponent* Camera = GetActiveCamera();
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
	if (bComboQueued && AttackMontages.IsValidIndex(ComboIndex + 1))
	{
		PlayComboAttack(ComboIndex + 1);
	}
}

void AProjectRCharacter::OnAttackMontageEnded(UAnimMontage* Montage, bool bInterrupted)
{
	// 다음 타로 넘어가며 끊긴 경우는 콤보가 이어지는 중이다.
	if (AttackMontages.IsValidIndex(ComboIndex) && Montage == AttackMontages[ComboIndex])
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
	// 기본 공격 중이면 콤보를 끊고 스킬을 쓴다(몽타주가 바뀌며 콤보 정리는 끝 이벤트가 한다).
	if (Skills->TryUseSlot(Slot))
	{
		ResetCombo();
	}
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
