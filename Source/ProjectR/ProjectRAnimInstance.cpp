#include "ProjectRAnimInstance.h"

#include "GameFramework/Character.h"
#include "ProjectRCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"

void UProjectRAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
	Super::NativeUpdateAnimation(DeltaSeconds);

	const ACharacter* Character = Cast<ACharacter>(TryGetPawnOwner());
	if (!Character)
	{
		return;
	}

	const AProjectRCharacter* Player = Cast<AProjectRCharacter>(Character);
	Speed = Player && !Player->ShouldUseLocomotionAnimation() ? 0.f : Character->GetVelocity().Size2D();
	bIsInAir = Character->GetCharacterMovement()->IsFalling();
}
