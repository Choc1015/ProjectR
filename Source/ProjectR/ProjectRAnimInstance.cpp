#include "ProjectRAnimInstance.h"

#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"

void UProjectRAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
	Super::NativeUpdateAnimation(DeltaSeconds);

	const ACharacter* Character = Cast<ACharacter>(TryGetPawnOwner());
	if (!Character)
	{
		return;
	}

	// 걷기·달리기 모션은 팔만 움직이게 만든 것이라 몸은 제자리에 서 있다.
	Speed = Character->GetVelocity().Size2D();
	bIsInAir = Character->GetCharacterMovement()->IsFalling();
}
