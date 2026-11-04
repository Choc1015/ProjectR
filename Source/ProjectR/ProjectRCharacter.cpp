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
#include "TimerManager.h"

AProjectRCharacter::AProjectRCharacter()
{
	// 몸 따라가기 모드에서만 켠다. 애니메이션이 본 위치를 갱신한 뒤 카메라를 옮긴다.
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = false;
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

	// 기본은 팔 부착 모드: 1인칭 템플릿처럼 메시를 카메라에 붙인다. 위치는 BP에서 눈높이에 맞춘다.
	GetMesh()->SetupAttachment(FirstPersonCamera);
	GetMesh()->SetRelativeLocationAndRotation(FVector(-5.f, 0.f, -160.f), FRotator(0.f, 180.f, 0.f));
	GetMesh()->SetCastShadow(false);

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

	ApplyCameraMode();
}

void AProjectRCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

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
	FRotator ViewRotation = GetControlRotation() + HeadOffset;
	ViewRotation.Pitch = FMath::ClampAngle(ViewRotation.Pitch, -89.f, 89.f);
	ViewRotation.Roll = 0.f;
	FirstPersonCamera->SetWorldLocationAndRotation(
		BodyMesh->GetBoneLocation(CameraBoneName) + ViewRotation.RotateVector(CameraBoneOffset), ViewRotation);
}

bool AProjectRCharacter::ShouldUseLocomotionAnimation() const
{
	return CameraMode == EFirstPersonCameraMode::CameraFollowsBody || bArmsFollowLocomotion;
}

void AProjectRCharacter::ApplyCameraMode()
{
	// 몸 전체가 보이는 모드에서만 그림자를 드리운다. 팔만 있을 때 그림자는 어색하다.
	GetMesh()->SetCastShadow(CameraMode == EFirstPersonCameraMode::CameraFollowsBody);
	// 몸 따라가기에서는 Tick이 마우스 시점과 머리 회전을 합쳐 직접 회전시킨다.
	FirstPersonCamera->bUsePawnControlRotation = CameraMode == EFirstPersonCameraMode::ArmsOnCamera;

	if (CameraMode == EFirstPersonCameraMode::CameraFollowsBody)
	{
		GetMesh()->AttachToComponent(GetCapsuleComponent(), FAttachmentTransformRules::KeepRelativeTransform);
		GetMesh()->SetRelativeTransform(BodyMeshTransform);
		bHasCameraBaseline = false;
		CameraBaselineDelay = 0.3f;
		SetActorTickEnabled(true);
		ApplyFirstPersonVisibility(BodyHiddenBoneNames, BodyHiddenMaterialSlotNames);
	}
	else
	{
		SetActorTickEnabled(false);
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

	if (const APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
			ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			Subsystem->AddMappingContext(DefaultMappingContext, 0);
		}
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
	}
}

void AProjectRCharacter::Move(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	const FRotator YawRotation(0.f, GetControlRotation().Yaw, 0.f);
	AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Axis.X);
}

void AProjectRCharacter::Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();
	AddControllerYawInput(Axis.X);
	AddControllerPitchInput(Axis.Y);
}

void AProjectRCharacter::Attack()
{
	if (AttackMontages.IsEmpty())
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

	const float Duration = AnimInstance->Montage_Play(Montage);
	if (Duration <= 0.f)
	{
		ResetCombo();
		return;
	}

	FOnMontageEnded EndDelegate;
	EndDelegate.BindUObject(this, &AProjectRCharacter::OnAttackMontageEnded);
	AnimInstance->Montage_SetEndDelegate(EndDelegate, Montage);

	FTimerManager& Timers = GetWorldTimerManager();
	Timers.SetTimer(HitTimer, this, &AProjectRCharacter::PerformHitTrace, Duration * HitTimeFraction, false);
	Timers.SetTimer(ComboTimer, this, &AProjectRCharacter::OnComboTime, Duration * ComboTimeFraction, false);
}

void AProjectRCharacter::PerformHitTrace()
{
	const FVector Start = FirstPersonCamera->GetComponentLocation();
	const FVector End = Start + FirstPersonCamera->GetForwardVector() * AttackRange;

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
			UGameplayStatics::ApplyPointDamage(HitActor, AttackDamage, GetActorForwardVector(), Hit,
				GetController(), this, nullptr);
		}
	}
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
	GetWorldTimerManager().ClearTimer(HitTimer);
	GetWorldTimerManager().ClearTimer(ComboTimer);
}
