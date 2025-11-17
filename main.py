import asyncio
import cli_manager
import external_file_io
import lcs_manager
import bfl_flux_manager

async def main():
    flag_1 = True
    lcs_manager.initialize_gpt_api()
    bfl_flux_manager.initialize_bfl_flux_api()

    external_file_io.assign_save_dir()
    external_file_io.assign_export_dir()
    external_file_io.open_project()
    while flag_1:
        flag_1 = await cli_manager.run_cli()

if __name__ == "__main__":
    asyncio.run(main())