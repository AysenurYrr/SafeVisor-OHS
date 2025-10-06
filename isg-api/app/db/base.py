# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa

# Import base models first
from app.models.role import Role  # noqa
from app.models.user import User  # noqa

# Import dependent models
from app.models.employee import Employee  # noqa
from app.models.employee import EmployeePhoto  # noqa
from app.models.camera import Camera  # noqa
from app.models.factory_area import FactoryArea  # noqa
from app.models.detection import Detection  # noqa
from app.models.violation import Violation  # noqa
from app.models.pose_alert import PoseAlert  # noqa