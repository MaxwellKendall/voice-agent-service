# Recipe Object Schema Consistency Report

## Executive Summary

**1. Is the recipe object consistent?** **NO**

The recipe object is **NOT consistent** across the codebase. There are significant discrepancies in field names, data types, and structure between different services and components.

## 2. Recommended Baseline Schema

Based on the analysis, I recommend using the **MCP TypeScript service** (`services/mcp_ts/src/types/recipe.ts`) as the baseline schema, as it appears to be the most comprehensive and well-structured definition.

### Baseline Schema (from MCP TypeScript)

```typescript
export interface Recipe {
  _id: ObjectId;
  link: string;
  source: string;
  title: string;
  original_title: string;
  ingredients: string;
  servings: string[];
  prep_time: string;
  cook_time: string;
  instruction_details: string[];
  nutrients: Nutrients;
  keywords: string;
  original_summary: string;
  cuisine: string;
  category: string;
  rating_count: number;
  rating: number;
  tools: string[];
  image_url: string;
  qualified: boolean;
  qualification_method: string;
  level_of_effort: number;
  relevance: Relevance;
  summary: string;
  vector_embedded?: boolean;
  vector_id?: string;
  embedding_prompt?: string;
}
```

## 3. Discrepancies by Location

### A. Scraper Service (`services/scraper/scraper/recipes/items.py`)

**Issues:**
- Uses `RecipeItem` class instead of interface
- Missing fields: `relevance`, `level_of_effort`, `vector_embedded`, `vector_id`, `embedding_prompt`
- Different field names: `instruction_details` vs `instructions` in other places
- `ingredients` is a generic `scrapy.Field()` instead of typed
- `servings` is single value instead of array
- Missing `original_title` field
- Missing `qualified` and `qualification_method` fields

**Fields Present:**
- `source`, `link`, `title`, `ingredients`, `prep_time`, `cook_time`, `servings`
- `instruction_details`, `nutrients`, `rating`, `rating_count`, `keywords`
- `summary`, `original_summary`, `image_url`, `tools`, `cuisine`, `category`

### B. MCP Python Service (`services/mcp/server.py` & `services/mcp/tools.py`)

**Issues:**
- No explicit schema definition - relies on MongoDB document structure
- Inconsistent field handling in `_get_recipe_by_id()` function
- Ingredients normalization logic suggests inconsistent data types
- Missing type safety and validation

**Fields Used:**
- `_id`, `title`, `summary`, `ingredients`, `instruction_details`
- `embedding_prompt` (new field), `prep_time`, `cook_time`
- Various other fields but without consistent typing

### C. Voice Cooking App (`services/voice-cooking-app/src/`)

**Issues:**
- Multiple different interfaces for the same concept
- Inconsistent field naming between components
- Type mismatches between API responses and component expectations

**Interfaces Found:**
1. `RecipeExtractionResponse` - for API responses
2. `RecipeByIdResponse` - for detailed recipe data
3. `RecipeData` - for component props
4. Various transformation functions to convert between formats

**Field Inconsistencies:**
- `prepTime` vs `prep_time` vs `prepTime`
- `cookTime` vs `cook_time` vs `cookTime`
- `instructions` vs `instruction_details`
- `description` vs `summary`
- `difficulty` vs `difficulty_level`
- `image` vs `image_url`

### D. MCP TypeScript Service (`services/mcp_ts/src/types/recipe.ts`)

**Status:** ✅ **Most Complete**
- Well-defined TypeScript interfaces
- Comprehensive field coverage
- Proper typing and validation
- Includes vector database integration fields

## 4. Ensuring Future Schema Consistency

### Immediate Actions Required:

1. **Create a Central Schema Definition**
   - Establish a single source of truth for recipe schema
   - Use the MCP TypeScript service as the baseline
   - Create shared type definitions that can be imported across services

2. **Implement Schema Validation**
   - Add runtime validation using libraries like Zod (TypeScript) or Pydantic (Python)
   - Validate all API inputs and outputs
   - Add database-level constraints

3. **Standardize Field Names**
   - Choose consistent naming convention (snake_case vs camelCase)
   - Update all services to use the same field names
   - Create migration scripts for existing data

4. **Create Data Transformation Layers**
   - Implement adapters to convert between different formats
   - Ensure backward compatibility during transition
   - Add comprehensive tests for data transformations

### Long-term Strategy:

1. **API Contract First Development**
   - Define OpenAPI/Swagger specifications for all recipe endpoints
   - Generate client libraries from these specifications
   - Use contract testing to ensure consistency

2. **Database Schema Standardization**
   - Migrate all recipe data to use consistent field names
   - Add database constraints and validation
   - Implement proper indexing for performance

3. **Monitoring and Validation**
   - Add schema validation to CI/CD pipelines
   - Implement runtime schema checking
   - Create alerts for schema violations

4. **Documentation and Training**
   - Document the canonical recipe schema
   - Create development guidelines
   - Train team on schema-first development

### Recommended Implementation Order:

1. **Phase 1:** Standardize MCP TypeScript service as baseline
2. **Phase 2:** Update voice-cooking-app to use consistent interfaces
3. **Phase 3:** Migrate MCP Python service to use typed schemas
4. **Phase 4:** Update scraper service to match baseline schema
5. **Phase 5:** Implement comprehensive validation and testing

### Tools and Technologies:

- **TypeScript:** Use strict typing and interfaces
- **Python:** Implement Pydantic models for validation
- **Database:** Add constraints and validation triggers
- **Testing:** Add schema validation tests to CI/CD
- **Documentation:** Use OpenAPI/Swagger for API documentation

This approach will ensure that recipe objects remain consistent across all services and prevent future discrepancies from surfacing.
