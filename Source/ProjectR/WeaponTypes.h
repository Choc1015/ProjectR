#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "WeaponTypes.generated.h"

class UAnimMontage;
class UNiagaraSystem;
class UStaticMesh;

/**
 * 무기 표(CSV) 한 줄. 행 이름이 무기 ID(Sword, Staff ...).
 * 원본 SourceArt/Data/Weapons.csv → /Game/Data/DT_Weapons
 */
USTRUCT(BlueprintType)
struct FWeaponRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	FText DisplayName;

	/** 손에 드는 메시. 비우면 BP_PlayerCharacter의 SwordMesh 메시 그대로 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	TSoftObjectPtr<UStaticMesh> Mesh;

	/** BP에서 맞춘 손잡이 위치(SwordMesh 상대 위치·회전) 위에 더하는 값(cm, 도) */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	FVector MeshOffsetLocation = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	FRotator MeshOffsetRotation = FRotator::ZeroRotator;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	FVector MeshScale = FVector::OneVector;

	/** 콤보 순서대로 재생할 공격 몽타주. 비우면 BP의 AttackMontages(검 콤보, 공격별 검 회전 포함) */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	TArray<TSoftObjectPtr<UAnimMontage>> AttackMontages;

	/** 켜면 타격 순간(Hit 노티파이)에 근접 판정 대신 시선 방향으로 탄을 쏜다. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	bool bProjectileAttack = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon|Projectile")
	TSoftObjectPtr<UStaticMesh> ProjectileMesh;

	/** 탄이 나오는 곳(무기 메시 기준 cm). 스태프는 수정 자리 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon|Projectile")
	FVector ProjectileMuzzle = FVector(0.0, 0.0, 90.0);

	/** cm/s */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon|Projectile")
	float ProjectileSpeed = 2500.f;

	/** 탄 피해 = 기본 공격 피해 × 이 값 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon|Projectile")
	float ProjectileDamageMultiplier = 1.f;

	/** 이 무기의 고유 스킬(F) ID. DT_Skills 행 이름 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Weapon")
	FName WeaponSkill;
};
