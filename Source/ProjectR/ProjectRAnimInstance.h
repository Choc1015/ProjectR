#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "ProjectRAnimInstance.generated.h"

/**
 * 플레이어 애님 블루프린트의 부모. AnimGraph가 쓰는 이동 값을 매 프레임 채운다.
 */
UCLASS()
class PROJECTR_API UProjectRAnimInstance : public UAnimInstance
{
	GENERATED_BODY()

public:
	virtual void NativeUpdateAnimation(float DeltaSeconds) override;

protected:
	/** 수평 이동 속도(cm/s). */
	UPROPERTY(BlueprintReadOnly, Category = "Locomotion")
	float Speed = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Locomotion")
	bool bIsInAir = false;
};
