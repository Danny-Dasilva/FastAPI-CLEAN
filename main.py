from fastapi import Depends, FastAPI
from strawberry import Schema
from strawberry.fastapi import GraphQLRouter

from configs.Environment import get_environment_variables
from configs.GraphQL import get_graphql_context
from metadata.Tags import Tags
from routers.v1.AuthorRouter import AuthorRouter
from schemas.graphql.Query import Query
from schemas.graphql.Mutation import Mutation
from config import config
# Application Environment Configuration

# Core Application Instance
app = FastAPI(
    title="test",
    version="0.0.0",
    openapi_tags=Tags,
)

# Add Routers
app.include_router(AuthorRouter)

# GraphQL Schema and Application Instance
schema = Schema(query=Query, mutation=Mutation)
graphql = GraphQLRouter(
    schema,
    graphiql=True,
    context_getter=get_graphql_context,
)

# Integrate GraphQL Application to the Core one
app.include_router(
    graphql,
    prefix="/graphql",
    include_in_schema=False,
)

if __name__ == "__main__":
    # Installed Packages
    import uvicorn

    uvicorn.run("main:app", reload=True, log_level="debug", use_colors=True)
