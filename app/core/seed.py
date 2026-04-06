import asyncio
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.dock_door import DockDoor
from app.core.security import get_password_hash

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding process started...")

        # 1. Create a Default Admin User (if not exists)
        result = await db.execute(select(User).filter(User.username == "admin_ali"))
        admin = result.scalars().first()
        
        if not admin:
            admin = User(
                username="admin_ali",
                email="ali@yard-system.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                region_id=1,
                is_active=True
            )
            db.add(admin)
            print("✅ Admin user created: admin_ali / admin123")
        else:
            print("ℹ️ Admin user already exists.")

        # 2. Create Sample Dock Doors
        result = await db.execute(select(DockDoor).filter(DockDoor.region_id == 1))
        existing_doors = result.scalars().all()
        
        if not existing_doors:
            doors = [
                DockDoor(door_number=f"D-0{i}", region_id=1, is_active=True)
                for i in range(1, 6)
            ]
            db.add_all(doors)
            print("✅ 5 sample Dock Doors added.")
        else:
            print("ℹ️ Dock doors already exist.")

        await db.commit()
        print("🚀 Seeding process completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())