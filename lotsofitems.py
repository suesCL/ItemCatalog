from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Items, Base, Category, User

engine = create_engine('sqlite:///categoryitemswithuser.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


############## category for running
# category1 = Category(name="Running")
# session.add(category1)
# session.commit()

# Item1 = Items(name="running shoes", description="Nike Air Contact",
                     # price="$56.50", category=category1)

# session.add(Item1)
# session.commit()


# Item2 = Items(name="women running top", description="Nike swoosh blue top in Large",
                     # price="$15.50", category=category1)

# session.add(Item2)
# session.commit()

# Item3 = Items(name="women running shorts", description="Nike blue shorts in Large",
                     # price="$27.50", category=category1)

# session.add(Item3)
# session.commit()


############## category for Climbing
# category2 = Category(name="Climbing")
# session.add(category2)
# session.commit()

# Item1 = Items(name="climbing pole", description="Carbon fiber Marnot black pole",
                     # price="$25", category=category2)

# session.add(Item1)
# session.commit()


# Item2 = Items(name="climbing shoes", description="Women FIFA Red 37 size",
                     # price="$60.50", category=category2)

# session.add(Item2)
# session.commit()

# Item3 = Items(name="climbing harness", description="Black Diamond Momentum Climbing Harness - Men's",
                     # price="$45.50", category=category2)

# session.add(Item3)
# session.commit()


##################### delete account 
# user1 = session.query(User).filter_by(username = "Zhenzhen Su").first()
# session.delete(user1)
# session.commit()

# Users = session.query(User).all()
# for i in Users:
	# print i.username + " " + i.email
	
	
################################
categories = session.query(Category).all()
for i in categories:
	print str(i.id) + " " + i.name

items = session.query(Items).all()
for i in items:
	print str(i.id) + " " + i.name
