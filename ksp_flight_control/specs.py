from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ThermalLimits:
    max_temp: float


@dataclass(frozen=True)
class SemiDeploymentSpec:
    drag: float
    min_pressure: float


@dataclass(frozen=True)
class FullDeploymentSpec:
    drag: float
    deploy_altitude: float


@dataclass(frozen=True)
class DeploymentSpec:
    semi: SemiDeploymentSpec
    full: FullDeploymentSpec


@dataclass(frozen=True)
class SafetySpec:
    max_safe_full_deploy_speed: float
    impact_tolerance: float


@dataclass(frozen=True)
class BehaviorSpec:
    requires_activation: bool
    requires_command_module: bool
    role: str
    deployment_priority: int
    deployment_stages: tuple[str, ...]
    slow_transition_to_full_deploy: bool
    significant_altitude_loss_during_deploy: bool
    full_deploy_delay_seconds: float


@dataclass(frozen=True)
class ParachuteSpec:
    part_name: str
    part_type: str
    mass: float
    cost: float
    drag_coefficient: float
    thermal_limits: ThermalLimits
    deployment: DeploymentSpec
    safety: SafetySpec
    behavior: BehaviorSpec


@dataclass(frozen=True)
class ConstantsConfig:
    standard_atmosphere_pa: float
    kerbin_surface_gravity_mps2: float
    ton_to_kg: float


@dataclass(frozen=True)
class PIDConfig:
    controllers: dict


@dataclass(frozen=True)
class SimPhysicsConfig:
    @dataclass(frozen=True)
    class AutoTriggerPolicy:
        trigger_in_safe: bool
        trigger_in_risky: bool
        trigger_in_unrecoverable: bool

    parachute_full_deploy_delay_seconds: float
    significant_altitude_loss_during_deploy: bool
    default_safe_vertical_speed_mps: float
    time_step_seconds: float
    atmosphere_scale_height_m: float
    surface_density_kgpm3: float
    base_drag_area_m2: float
    parachute_drag_area_scale: float
    descent_detection_vertical_speed_mps: float
    narrow_window_altitude_margin_m: float
    unrecoverable_altitude_m: float
    default_policy_mode: str
    policy_modes: dict[str, AutoTriggerPolicy]

    def policy_for(self, mode: str | None = None) -> AutoTriggerPolicy:
        selected_mode = self.default_policy_mode if mode is None else mode
        return self.policy_modes[selected_mode]


@dataclass(frozen=True)
class MathConfig:
    equations: dict[str, str]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class PartsCatalog:
    default_parachute_id: str
    all_parachutes: dict[str, ParachuteSpec]

    @property
    def default_parachute(self) -> ParachuteSpec:
        return self.all_parachutes[self.default_parachute_id]

    def by_role(self, role: str) -> list[ParachuteSpec]:
        return [spec for spec in self.all_parachutes.values() if spec.behavior.role == role]


@dataclass(frozen=True)
class ProjectConfig:
    constants: ConstantsConfig
    sim_physics: SimPhysicsConfig
    pid: PIDConfig
    math: MathConfig
    parts: PartsCatalog


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_constants() -> ConstantsConfig:
    data = _load_yaml(CONFIG_DIR / "constants.yaml")
    return ConstantsConfig(
        standard_atmosphere_pa=data["atmosphere"]["standard_pressure_pa"],
        kerbin_surface_gravity_mps2=data["gravity"]["kerbin_surface_mps2"],
        ton_to_kg=data["units"]["ton_to_kg"],
    )


def _load_sim_physics() -> SimPhysicsConfig:
    data = _load_yaml(CONFIG_DIR / "sim_physics.yaml")
    policy_modes = {
        name: SimPhysicsConfig.AutoTriggerPolicy(
            trigger_in_safe=policy["trigger_in_safe"],
            trigger_in_risky=policy["trigger_in_risky"],
            trigger_in_unrecoverable=policy["trigger_in_unrecoverable"],
        )
        for name, policy in data["auto_trigger"]["policy_modes"].items()
    }
    return SimPhysicsConfig(
        parachute_full_deploy_delay_seconds=data["parachutes"]["full_deploy_delay_seconds"],
        significant_altitude_loss_during_deploy=data["parachutes"]["significant_altitude_loss_during_deploy"],
        default_safe_vertical_speed_mps=data["descent"]["default_safe_vertical_speed_mps"],
        time_step_seconds=data["engine"]["time_step_seconds"],
        atmosphere_scale_height_m=data["engine"]["atmosphere_scale_height_m"],
        surface_density_kgpm3=data["engine"]["surface_density_kgpm3"],
        base_drag_area_m2=data["engine"]["base_drag_area_m2"],
        parachute_drag_area_scale=data["engine"]["parachute_drag_area_scale"],
        descent_detection_vertical_speed_mps=data["auto_trigger"]["descent_detection_vertical_speed_mps"],
        narrow_window_altitude_margin_m=data["auto_trigger"]["narrow_window_altitude_margin_m"],
        unrecoverable_altitude_m=data["auto_trigger"]["unrecoverable_altitude_m"],
        default_policy_mode=data["auto_trigger"]["default_policy_mode"],
        policy_modes=policy_modes,
    )


def _load_pid() -> PIDConfig:
    data = _load_yaml(CONFIG_DIR / "pid_controllers.yaml")
    return PIDConfig(controllers=data["controllers"])


def _load_math() -> MathConfig:
    data = _load_yaml(CONFIG_DIR / "math_equations.yaml")
    return MathConfig(
        equations=data["equations"],
        notes=tuple(data.get("notes", [])),
    )


def _build_parachute_spec(data: dict, sim_physics: SimPhysicsConfig) -> ParachuteSpec:
    behavior_notes = data["behavior"]["notes"]
    return ParachuteSpec(
        part_name=data["part_name"],
        part_type=data["type"],
        mass=data["mass"],
        cost=data["cost"],
        drag_coefficient=data["drag_coefficient"],
        thermal_limits=ThermalLimits(max_temp=data["thermal_limits"]["max_temp"]),
        deployment=DeploymentSpec(
            semi=SemiDeploymentSpec(
                drag=data["deployment"]["semi"]["drag"],
                min_pressure=data["deployment"]["semi"]["min_pressure"],
            ),
            full=FullDeploymentSpec(
                drag=data["deployment"]["full"]["drag"],
                deploy_altitude=data["deployment"]["full"]["deploy_altitude"],
            ),
        ),
        safety=SafetySpec(
            max_safe_full_deploy_speed=data["safety"]["max_safe_full_deploy_speed"],
            impact_tolerance=data["safety"]["impact_tolerance"],
        ),
        behavior=BehaviorSpec(
            requires_activation=data["behavior"]["requires_activation"],
            requires_command_module=data["behavior"]["requires_command_module"],
            role=data["behavior"]["role"],
            deployment_priority=data["behavior"]["deployment_priority"],
            deployment_stages=tuple(data["behavior"]["deployment_stages"]),
            slow_transition_to_full_deploy=behavior_notes["slow_transition_to_full_deploy"],
            significant_altitude_loss_during_deploy=behavior_notes["significant_altitude_loss_during_deploy"],
            full_deploy_delay_seconds=sim_physics.parachute_full_deploy_delay_seconds,
        ),
    )


def _load_parts(sim_physics: SimPhysicsConfig) -> PartsCatalog:
    index = _load_yaml(CONFIG_DIR / "parts" / "index.yaml")
    parachute_index = index["parachutes"]
    parachutes = {}

    for parachute_id, filename in parachute_index["files"].items():
        data = _load_yaml(CONFIG_DIR / "parts" / filename)
        parachutes[parachute_id] = _build_parachute_spec(data, sim_physics)

    return PartsCatalog(
        default_parachute_id=parachute_index["default"],
        all_parachutes=parachutes,
    )


def load_project_config() -> ProjectConfig:
    sim_physics = _load_sim_physics()
    return ProjectConfig(
        constants=_load_constants(),
        sim_physics=sim_physics,
        pid=_load_pid(),
        math=_load_math(),
        parts=_load_parts(sim_physics),
    )


PROJECT_CONFIG = load_project_config()
TEST_DROGUE_PARACHUTE = PROJECT_CONFIG.parts.all_parachutes["drogue_parachute"]
MK16_PARACHUTE = PROJECT_CONFIG.parts.all_parachutes["mk16_parachute"]
DEFAULT_PARACHUTE_SPEC = PROJECT_CONFIG.parts.default_parachute
STANDARD_ATMOSPHERE_PA = PROJECT_CONFIG.constants.standard_atmosphere_pa
