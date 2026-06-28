"""DORA RoI template models — GENERATED from spec/_extracted/template_fields.json.

Do NOT hand-edit. Regenerate: uv run python scripts/gen_models.py

- Field name  = snake_case(EBA label); alias = xBRL column code (the header in xBRL-CSV).
- All fields Optional for now; mandatory-ness + enums come from the validation rules and
  the 'list of possible values' (spec/) — bound in a later pass (no fabrication here).
- Central key: B_02.01.contractual_arrangement_reference_number; the same field in
  B_02.02/02.03/03.01/03.02/03.03/04.01/05.02/07.01 is a foreign key into it.
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field


class RoiTemplate(BaseModel):
    """Base for all RoI template rows. Accepts both field name and xBRL alias."""
    model_config = ConfigDict(populate_by_name=True)


class B_01_01(RoiTemplate):
    """B_01.01 - Entity maintaining the register of information"""
    TEMPLATE_ID: ClassVar[str] = "B_01.01"
    lei_of_the_entity_maintaining_the_register_of_information: Optional[str] = Field(None, alias="c0010", description="LEI of the entity maintaining the register of information")
    name_of_the_entity: Optional[str] = Field(None, alias="c0020", description="Name of the entity")
    country_of_the_entity: Optional[str] = Field(None, alias="c0030", description="Country of the entity")
    type_of_entity: Optional[str] = Field(None, alias="c0040", description="Type of entity")
    competent_authority: Optional[str] = Field(None, alias="c0050", description="Competent Authority")
    date_of_the_reporting: Optional[datetime.date] = Field(None, alias="c0060", description="Date of the reporting")


class B_01_02(RoiTemplate):
    """B_01.02 - List of entities within the scope of the register of information"""
    TEMPLATE_ID: ClassVar[str] = "B_01.02"
    lei_of_the_entity: Optional[str] = Field(None, alias="c0010", description="LEI of the entity")
    name_of_the_entity: Optional[str] = Field(None, alias="c0020", description="Name of the entity")
    country_of_the_entity: Optional[str] = Field(None, alias="c0030", description="Country of the entity")
    type_of_entity: Optional[str] = Field(None, alias="c0040", description="Type of entity")
    hierarchy_of_the_entity_within_the_group_where_applicable: Optional[str] = Field(None, alias="c0050", description="Hierarchy of the entity within the group (where applicable)")
    lei_of_the_direct_parent_undertaking_of_the_entity: Optional[str] = Field(None, alias="c0060", description="LEI of the direct parent undertaking of the entity")
    date_of_last_update: Optional[datetime.date] = Field(None, alias="c0070", description="Date of last update")
    date_of_integration_in_the_register_of_information: Optional[datetime.date] = Field(None, alias="c0080", description="Date of integration in the Register of information")
    date_of_deletion_in_the_register_of_information: Optional[datetime.date] = Field(None, alias="c0090", description="Date of deletion in the Register of information")
    currency: Optional[str] = Field(None, alias="c0100", description="Currency")
    value_of_total_assets_of_the_financial_entity: Optional[Decimal] = Field(None, alias="c0110", description="Value of total assets - of the financial entity")


class B_01_03(RoiTemplate):
    """B_01.03 - List of branches"""
    TEMPLATE_ID: ClassVar[str] = "B_01.03"
    identification_code_of_the_branch: Optional[str] = Field(None, alias="c0010", description="Identification code of the branch")
    lei_of_the_financial_entity_head_office_of_the_branch: Optional[str] = Field(None, alias="c0020", description="LEI of the financial entity head office of the branch")
    name_of_the_branch: Optional[str] = Field(None, alias="c0030", description="Name of the branch")
    country_of_the_branch: Optional[str] = Field(None, alias="c0040", description="Country of the branch")


class B_02_01(RoiTemplate):
    """B_02.01 - Contractual arrangements – General Information"""
    TEMPLATE_ID: ClassVar[str] = "B_02.01"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    type_of_contractual_arrangement: Optional[str] = Field(None, alias="c0020", description="Type of contractual arrangement")
    overarching_contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0030", description="Overarching contractual arrangement reference number")
    currency_of_the_amount_reported_in_rt_02_01_0050: Optional[str] = Field(None, alias="c0040", description="Currency of the amount reported in RT.02.01.0050")
    annual_expense_or_estimated_cost_of_the_contractual_arrangement_for_the_past_year: Optional[Decimal] = Field(None, alias="c0050", description="Annual expense or estimated cost of the contractual arrangement for the past year")


class B_02_02(RoiTemplate):
    """B_02.02 - Contractual arrangements – Specific information"""
    TEMPLATE_ID: ClassVar[str] = "B_02.02"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    lei_of_the_entity_making_use_of_the_ict_service_s: Optional[str] = Field(None, alias="c0020", description="LEI of the entity making use of the ICT service(s)")
    identification_code_of_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0030", description="Identification code of the ICT third-party service provider")
    type_of_code_to_identify_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0040", description="Type of code to identify the ICT third-party service provider")
    function_identifier: Optional[str] = Field(None, alias="c0050", description="Function identifier")
    type_of_ict_services: Optional[str] = Field(None, alias="c0060", description="Type of ICT services")
    start_date_of_the_contractual_arrangement: Optional[datetime.date] = Field(None, alias="c0070", description="Start date of the contractual arrangement")
    end_date_of_the_contractual_arrangement: Optional[datetime.date] = Field(None, alias="c0080", description="End date of the contractual arrangement")
    reason_of_the_termination_or_ending_of_the_contractual_arrangement: Optional[str] = Field(None, alias="c0090", description="Reason of the termination or ending of the contractual arrangement")
    notice_period_for_the_financial_entity_making_use_of_the_ict_service_s: Optional[str] = Field(None, alias="c0100", description="Notice period for the financial entity making use of the ICT service(s)")
    notice_period_for_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0110", description="Notice period for the ICT third-party service provider")
    country_of_the_governing_law_of_the_contractual_arrangement: Optional[str] = Field(None, alias="c0120", description="Country of the governing law of the contractual arrangement")
    country_of_provision_of_the_ict_services: Optional[str] = Field(None, alias="c0130", description="Country of provision of the ICT services")
    storage_of_data: Optional[str] = Field(None, alias="c0140", description="Storage of data")
    location_of_the_data_at_rest_storage: Optional[str] = Field(None, alias="c0150", description="Location of the data at rest (storage)")
    location_of_management_of_the_data_processing: Optional[str] = Field(None, alias="c0160", description="Location of management of the data (processing)")
    sensitiveness_of_the_data_stored_by_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0170", description="Sensitiveness of the data stored by the ICT third-party service provider")
    level_of_reliance_on_the_ict_service_supporting_the_critical_or_important_function: Optional[str] = Field(None, alias="c0180", description="Level of reliance on the ICT service supporting the critical or important function.")


class B_02_03(RoiTemplate):
    """B_02.03 - List of intra-group contractual arrangements"""
    TEMPLATE_ID: ClassVar[str] = "B_02.03"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    contractual_arrangement_linked_to_the_contractual_arrangement_referred_in_rt_02_03_0010: Optional[str] = Field(None, alias="c0020", description="Contractual arrangement linked to the contractual arrangement referred in RT.02.03.0010")
    link: Optional[str] = Field(None, alias="c0030", description="Link")


class B_03_01(RoiTemplate):
    """B_03.01 - Entities signing the Contractual arrangements for receiving ICT service(s) or on behalf of the entities making use of the ICT service(s)"""
    TEMPLATE_ID: ClassVar[str] = "B_03.01"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    lei_of_the_entity_signing_the_contractual_arrangement: Optional[str] = Field(None, alias="c0020", description="LEI of the entity signing the contractual arrangement")
    link: Optional[str] = Field(None, alias="c0030", description="Link")


class B_03_02(RoiTemplate):
    """B_03.02 - ICT third-party service providers signing the Contractual arrangements for providing ICT service(s)"""
    TEMPLATE_ID: ClassVar[str] = "B_03.02"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    identification_code_of_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0020", description="Identification code of ICT third-party service provider")
    type_of_code_to_identify_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0030", description="Type of code to identify the ICT third-party service provider")


class B_03_03(RoiTemplate):
    """B_03.03 - Entities signing the Contractual arrangements for providing ICT service(s) to other entity within the scope of consolidation"""
    TEMPLATE_ID: ClassVar[str] = "B_03.03"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    lei_of_the_entity_providing_ict_services: Optional[str] = Field(None, alias="c0020", description="LEI of the entity providing ICT services")
    link: Optional[str] = Field(None, alias="c0031", description="Link")


class B_04_01(RoiTemplate):
    """B_04.01 - Entities making use of the ICT services"""
    TEMPLATE_ID: ClassVar[str] = "B_04.01"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    lei_of_the_entity_making_use_of_the_ict_service_s: Optional[str] = Field(None, alias="c0020", description="LEI of the entity making use of the ICT service(s)")
    nature_of_the_entity_making_use_of_the_ict_service_s: Optional[str] = Field(None, alias="c0030", description="Nature of the entity making use of the ICT service(s)")
    identification_code_of_the_branch: Optional[str] = Field(None, alias="c0040", description="Identification code of the branch")


class B_05_01(RoiTemplate):
    """B_05.01 - ICT third-party service providers"""
    TEMPLATE_ID: ClassVar[str] = "B_05.01"
    identification_code_of_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0010", description="Identification code of ICT third-party service provider")
    type_of_code_to_identify_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0020", description="Type of code to identify the ICT third-party service provider")
    additional_identification_code_of_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0030", description="Additional identification code of ICT third-party service provider")
    type_of_additional_identification_code_of_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0040", description="Type of additional identification code of the ICT third-party service provider")
    legal_name_of_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0050", description="Legal name of the ICT third-party service provider")
    name_of_the_ict_third_party_service_provider_in_latin_alphabet: Optional[str] = Field(None, alias="c0060", description="Name of the ICT third-party service provider in Latin alphabet")
    type_of_person_of_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0070", description="Type of person of the ICT third-party service provider")
    country_of_the_ict_third_party_service_provider_s_headquarters: Optional[str] = Field(None, alias="c0080", description="Country of the ICT third-party service provider’s headquarters")
    currency_of_the_amount_reported_in_rt_05_01_0070: Optional[str] = Field(None, alias="c0090", description="Currency of the amount reported in RT.05.01.0070")
    total_annual_expense_or_estimated_cost_of_the_ict_third_party_service_provider: Optional[Decimal] = Field(None, alias="c0100", description="Total annual expense or estimated cost of the ICT third-party service provider")
    identification_code_of_the_ict_third_party_service_provider_s_ultimate_parent_undertaking: Optional[str] = Field(None, alias="c0110", description="Identification code of the ICT third-party service provider’s ultimate parent undertaking")
    type_of_code_to_identify_the_ict_third_party_service_provider_s_ultimate_parent_undertaking: Optional[str] = Field(None, alias="c0120", description="Type of code to identify the ICT third-party service provider’s ultimate parent undertaking")


class B_05_02(RoiTemplate):
    """B_05.02 - ICT service supply chains"""
    TEMPLATE_ID: ClassVar[str] = "B_05.02"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    type_of_ict_services: Optional[str] = Field(None, alias="c0020", description="Type of ICT services")
    identification_code_of_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0030", description="Identification code of the ICT third-party service provider")
    type_of_code_to_identify_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0040", description="Type of code to identify the ICT third-party service provider")
    rank: Optional[str] = Field(None, alias="c0050", description="Rank")
    identification_code_of_the_recipient_of_sub_contracted_ict_services: Optional[str] = Field(None, alias="c0060", description="Identification code of the recipient of sub-contracted ICT services")
    type_of_code_to_identify_the_recipient_of_sub_contracted_ict_services: Optional[str] = Field(None, alias="c0070", description="Type of code to identify the recipient of sub-contracted ICT services")


class B_06_01(RoiTemplate):
    """B_06.01 - Functions identification"""
    TEMPLATE_ID: ClassVar[str] = "B_06.01"
    function_identifier: Optional[str] = Field(None, alias="c0010", description="Function Identifier")
    licenced_activity: Optional[str] = Field(None, alias="c0020", description="Licenced activity")
    function_name: Optional[str] = Field(None, alias="c0030", description="Function name")
    lei_of_the_financial_entity: Optional[str] = Field(None, alias="c0040", description="LEI of the financial entity")
    criticality_or_importance_assessment: Optional[str] = Field(None, alias="c0050", description="Criticality or importance assessment")
    reasons_for_criticality_or_importance: Optional[str] = Field(None, alias="c0060", description="Reasons for criticality or importance")
    date_of_the_last_assessment_of_criticality_or_importance: Optional[datetime.date] = Field(None, alias="c0070", description="Date of the last assessment of criticality or importance")
    recovery_time_objective_of_the_function: Optional[str] = Field(None, alias="c0080", description="Recovery time objective of the function")
    recovery_point_objective_of_the_function: Optional[str] = Field(None, alias="c0090", description="Recovery point objective of the function")
    impact_of_discontinuing_the_function: Optional[str] = Field(None, alias="c0100", description="Impact of discontinuing the function")


class B_07_01(RoiTemplate):
    """B_07.01 - Assessment of the ICT services"""
    TEMPLATE_ID: ClassVar[str] = "B_07.01"
    contractual_arrangement_reference_number: Optional[str] = Field(None, alias="c0010", description="Contractual arrangement reference number")
    identification_code_of_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0020", description="Identification code of the ICT third-party service provider")
    type_of_code_to_identify_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0030", description="Type of code to identify the ICT third-party service provider")
    type_of_ict_services: Optional[str] = Field(None, alias="c0040", description="Type of ICT services")
    substitutability_of_the_ict_third_party_service_provider: Optional[str] = Field(None, alias="c0050", description="Substitutability of the ICT third-party service provider")
    reason_if_the_ict_third_party_service_provider_is_considered_not_substitutable_or_difficult_to_be_substitutable: Optional[str] = Field(None, alias="c0060", description="Reason if the ICT third-party service provider is considered not substitutable or difficult to be substitutable")
    date_of_the_last_audit_on_the_ict_third_party_service_provider: Optional[datetime.date] = Field(None, alias="c0070", description="Date of the last audit on the ICT third-party service provider")
    existence_of_an_exit_plan: Optional[str] = Field(None, alias="c0080", description="Existence of an exit plan")
    possibility_of_reintegration_of_the_contracted_ict_service: Optional[str] = Field(None, alias="c0090", description="Possibility of reintegration of the contracted ICT service")
    impact_of_discontinuing_the_ict_services: Optional[str] = Field(None, alias="c0100", description="Impact of discontinuing the ICT services")
    are_there_alternative_ict_third_party_service_providers_identified: Optional[str] = Field(None, alias="c0110", description="Are there alternative ICT third-party service providers identified?")
    identification_of_alternative_ict_tpp: Optional[str] = Field(None, alias="c0120", description="Identification of alternative ICT TPP")


class B_99_01(RoiTemplate):
    """B_99.01 - Definitions from Entities making use of the ICT Services"""
    TEMPLATE_ID: ClassVar[str] = "B_99.01"
    standalone_arrangement: Optional[str] = Field(None, alias="c0010", description="Standalone arrangement")
    overarching_arrangement: Optional[str] = Field(None, alias="c0020", description="Overarching arrangement")
    subsequent_or_associated_arrangement: Optional[str] = Field(None, alias="c0030", description="Subsequent or associated arrangement")
    low: Optional[str] = Field(None, alias="c0040", description="Low")
    medium: Optional[str] = Field(None, alias="c0050", description="Medium")
    high: Optional[str] = Field(None, alias="c0060", description="High")
    low_c0070: Optional[str] = Field(None, alias="c0070", description="Low")
    medium_c0080: Optional[str] = Field(None, alias="c0080", description="Medium")
    high_c0090: Optional[str] = Field(None, alias="c0090", description="High")
    not_substitutable: Optional[str] = Field(None, alias="c0100", description="Not substitutable")
    highly_complex_substitutability: Optional[str] = Field(None, alias="c0110", description="Highly complex substitutability")
    medium_complexity_in_terms_of_substitutability: Optional[str] = Field(None, alias="c0120", description="Medium complexity in terms of substitutability")
    easily_substitutable: Optional[str] = Field(None, alias="c0130", description="Easily substitutable")
    easy: Optional[str] = Field(None, alias="c0140", description="Easy")
    difficult: Optional[str] = Field(None, alias="c0150", description="Difficult")
    highly_complex: Optional[str] = Field(None, alias="c0160", description="Highly complex")
    low_c0170: Optional[str] = Field(None, alias="c0170", description="Low")
    medium_c0180: Optional[str] = Field(None, alias="c0180", description="Medium")
    high_c0190: Optional[str] = Field(None, alias="c0190", description="High")


TEMPLATES: dict[str, type[RoiTemplate]] = {"B_01.01": B_01_01, "B_01.02": B_01_02, "B_01.03": B_01_03, "B_02.01": B_02_01, "B_02.02": B_02_02, "B_02.03": B_02_03, "B_03.01": B_03_01, "B_03.02": B_03_02, "B_03.03": B_03_03, "B_04.01": B_04_01, "B_05.01": B_05_01, "B_05.02": B_05_02, "B_06.01": B_06_01, "B_07.01": B_07_01, "B_99.01": B_99_01}
