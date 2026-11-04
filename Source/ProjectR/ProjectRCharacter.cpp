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
#include "TimerManager.h"

AProjectRCharacter::AProjectRCharacter()
{
	GetCapsuleComponent()->InitCapsuleSize(35.f, 90.f);

	bUseControllerRotationYaw = true;
	GetCharacterMovement()->MaxWalkSpeed = 450.f;
	GetCharacterMovement()->bOrientRotationToMovement = false;

	// 메시 원점은 발바닥, 미사모 임포트 결과 정면이 -X → 캡슐 바닥에 맞추고 +X를 보게 돌린다.
	GetMesh()->SetRelativeLocationAndRotation(FVector(0.f, 0.f, -90.f), FRotator(0.f, 180.f, 0.f));

	FirstPersonCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
	FirstPersonCamera->SetupAttachment(GetCapsuleComponent());
	FirstPersonCamera->SetRelativeLocation(FVector(12.f, 0.f, 70.f));
	FirstPersonCamera->bUsePawnControlRotation = true;
	FirstPersonCamera->SetFieldOfView(90.f);

	SwordMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SwordMesh"));
	SwordMesh->SetupAttachment(GetMesh(), WeaponSocketName);
	SwordMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void AProjectRCharacter::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);

	// 블루프린트에서 소켓 이름을 바꿨을 수 있으니 다시 붙인다. 에디터 배치 시에도 손에 보이게 여기서 한다.
	SwordMesh->AttachToComponent(GetMesh(), FAttachmentTransformRules::KeepRelativeTransform, WeaponSocketName);
}

void AProjectRCharacter::BeginPlay()
{
	Super::BeginPlay();

	if (!HiddenHeadBoneName.IsNone() && GetMesh()->GetBoneIndex(HiddenHeadBoneName) != INDEX_NONE)
	{
		GetMesh()->HideBoneByName(HiddenHeadBoneName, PBO_None);
	}

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
