import xarray as xr
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
# import matplotlib as mpl
# from metpy.units import units
# from metpy.plots import SkewT
# import metpy
from pandas import read_csv, date_range
from time import perf_counter
from glob import glob
from matplotlib.style import use as usestyle
from importlib import reload
import makevids as mkv
from concurrent.futures import ProcessPoolExecutor
from os import path, mkdir
from functools import partial



from matplotlib import font_manager as fm
fontdir = "/home/ascheb/libfonts/*.ttf"
for fpath in glob(fontdir):
    print(fpath)
    fm.fontManager.addfont(fpath)

usestyle("/home/ascheb/paperplots.mplstyle")

def make_combplots(figprepath, fields, t):
    headpath = "/moonbow/ascheb/idealized/pastureconiforest-wind/rams_output/a-A-2022-06-17-060000-head.txt"
    # case = "unisuburb-wind/"
    # gprops = get_gprops(headpath, 1)
    ftime = t.strftime("%Y-%m-%d-%H%M%S")
    folderprepath = "/moonbow/ascheb/idealized/"
    print(ftime)
    afile_unipasture = xr.open_dataset(f"{folderprepath}unipasture-wind/ppfiles_paper/mvars-cart-{ftime}-g1.nc")
    afile_coniforest = xr.open_dataset(f"{folderprepath}coniforest-wind/ppfiles_paper/mvars-cart-{ftime}-g1.nc")
    afile_suburb = xr.open_dataset(f"{folderprepath}unisuburb-wind/ppfiles_paper/mvars-cart-{ftime}-g1.nc")
    afile_pastureconiforest = xr.open_dataset(f"{folderprepath}pastureconiforest-wind/ppfiles_paper/mvars-cart-{ftime}-g1.nc")
    afile_suburbconiforest = xr.open_dataset(f"{folderprepath}suburbconiforest-wind/ppfiles_paper/mvars-cart-{ftime}-g1.nc")
    afile_suburbpasture = xr.open_dataset(f"{folderprepath}suburbpasture-wind/ppfiles_paper/mvars-cart-{ftime}-g1.nc")
    # afile_pasturebroadforest = xr.open_dataset(f"{folderpath}pasturebroadforest-wind/processed_data/mergedvars_{ftime}.nc")
    if not path.exists(f"{figprepath}/"):
        mkdir(f"{figprepath}/")
    
    # fields = ["SrfTemp"]
    axlabels = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)"]
    for field in fields:
        fig, ((ax11, ax12, ax13), (ax21, ax22, ax23)) = plt.subplots(2, 3, figsize = (4, 5), dpi = 200, layout = "compressed", sharex = True, sharey = True)
        for i, ax in enumerate(fig.get_axes()):
            ax.set_aspect(1)
            ax.set_yticks([200, 300, 450, 600, 800], labels = ["-50 ", "0  ", "75 ", 150, 250])
            ax.set_xticks([0, 100, 200, 300, 400], labels = [-100, -50, 0, 50, 100])
            left, width = 0, 0.16
            bottom, height = 0.92, 0.08
            right = left + width
            top = bottom + height
            p = plt.Rectangle((left, bottom), width, height, fill=True, zorder = 3, edgecolor = "black", linewidth = 0.2, facecolor = "white")
            p.set_transform(ax.transAxes)
            p.set_clip_on(False)
            ax.add_patch(p)
            ax.text(left+0.5*width, bottom+0.5*height, axlabels[i], fontsize = 6.5, transform = ax.transAxes, horizontalalignment = "center", verticalalignment = "center")
        for ax in (ax11, ax21):
            ax.set_ylabel("Distance from Shore (km)")
            ax.tick_params(axis = "x", bottom = False, labelbottom = False, left = True, labelleft = True)
        ax22.set_xlabel("Distance from Center (km)")
        for ax in (ax12, ax13, ax23):
            ax.tick_params(axis = "both", bottom = False, left = False, labelbottom = False, labeltop = False, labelleft = False)
        ax22.tick_params(axis = "y", left = False, labelleft = False, bottom = True, labelbottom = True)
        # for ax in (ax21, ax22, ax23):
        #     forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
        #     ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
        # for ax in fig.get_axes():
        #     shoreline = ax.axhline(301, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
        #     ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "white", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
        ax11.set_title("Uniform Pasture (UP)", fontfamily = "Liberation Serif", y = 1.02)
        ax12.set_title("Uniform Forest (UF)", fontfamily = "Liberation Serif", y = 1.02)
        ax13.set_title("Uniform Suburb (US)", fontfamily = "Liberation Serif", y = 1.02)
        ax21.set_title("Pasture-Forest (PF)", fontfamily = "Liberation Serif", y = 1.02)
        ax22.set_title("Suburb-Forest (SF)", fontfamily = "Liberation Serif", y = 1.02)
        ax23.set_title("Suburb-Pasture (SP)", fontfamily = "Liberation Serif", y = 1.02)
        fig.get_layout_engine().set(h_pad = 0.05, hspace = 0.1)
        
        print(f"Plotting Field {field}")
        if field == "RainRate":
            fig.suptitle(f"Rain Rate at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
            rainbounds = [0, 0.1, 0.3, 0.5, 1.5, 2.5, 5.5, 7.5, 11.75, 15, 20, 25, 37.5, 50, 70]
            rainnorm = BoundaryNorm(boundaries = rainbounds, ncolors = 256, extend = "max")
            rainmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["RainPrecipRate"].where(afile_unipasture["RainPrecipRate"]>0.01).isel(y = slice(200,800)), cmap = "jet", norm = rainnorm)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["RainPrecipRate"].where(afile_coniforest["RainPrecipRate"]>0.01).isel(y = slice(200,800)), cmap = "jet", norm = rainnorm)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["RainPrecipRate"].where(afile_suburb["RainPrecipRate"]>0.01).isel(y = slice(200,800)), cmap = "jet", norm = rainnorm)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["RainPrecipRate"].where(afile_pastureconiforest["RainPrecipRate"]>0.01).isel(y = slice(200,800)), cmap = "jet", norm = rainnorm)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["RainPrecipRate"].where(afile_suburbconiforest["RainPrecipRate"]>0.01).isel(y = slice(200,800)), cmap = "jet", norm = rainnorm)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["RainPrecipRate"].where(afile_suburbpasture["RainPrecipRate"]>0.01).isel(y = slice(200,800)), cmap = "jet", norm = rainnorm)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "black", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "black", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(rainmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "max"); cbar.set_label(r"Rain Rate $(mm \ hr^{-1})$")
            fig.savefig(f"{figprepath}/rainrate_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "LhFlux":
            fig.suptitle(f"Surface Latent Heat Flux at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
            lhmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["LatentHeatFlux"].isel(y = slice(200,800)), cmap = "BrBG", vmin = -500, vmax = 500)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["LatentHeatFlux"].isel(y = slice(200,800)), cmap = "BrBG", vmin = -500, vmax = 500)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["LatentHeatFlux"].isel(y = slice(200,800)), cmap = "BrBG", vmin = -500, vmax = 500)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["LatentHeatFlux"].isel(y = slice(200,800)), cmap = "BrBG", vmin = -500, vmax = 500)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["LatentHeatFlux"].isel(y = slice(200,800)), cmap = "BrBG", vmin = -500, vmax = 500)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["LatentHeatFlux"].isel(y = slice(200,800)), cmap = "BrBG", vmin = -500, vmax = 500)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "black", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "black", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(lhmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "both"); cbar.set_label(r"Latent Heat Flux $(W \ m^{-2})$")
            fig.savefig(f"{figprepath}/lhflux_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "ShFlux":
            fig.suptitle(f"Surface Sensible Heat Flux at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
            shmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["SensibleHeatFlux"].isel(y = slice(200,800)), cmap = "bwr", vmin = -750, vmax = 750)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["SensibleHeatFlux"].isel(y = slice(200,800)), cmap = "bwr", vmin = -750, vmax = 750)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["SensibleHeatFlux"].isel(y = slice(200,800)), cmap = "bwr", vmin = -750, vmax = 750)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["SensibleHeatFlux"].isel(y = slice(200,800)), cmap = "bwr", vmin = -750, vmax = 750)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["SensibleHeatFlux"].isel(y = slice(200,800)), cmap = "bwr", vmin = -750, vmax = 750)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["SensibleHeatFlux"].isel(y = slice(200,800)), cmap = "bwr", vmin = -750, vmax = 750)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "black", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "black", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(shmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "both"); cbar.set_label(r"Sensible Heat Flux $(W \ m^{-2})$")
            fig.savefig(f"{figprepath}/shflux_{t.hour}{str(t.minute).zfill(2)}z.png")
        
        elif field == "Bowen":
            fig.suptitle(f"Bowen Ratio at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
            bwmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (afile_unipasture["SensibleHeatFlux"]/afile_unipasture["LatentHeatFlux"]).isel(y = slice(200,800)), cmap = "Spectral_r", vmin = 0, vmax = 2)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (afile_coniforest["SensibleHeatFlux"]/afile_coniforest["LatentHeatFlux"]).isel(y = slice(200,800)), cmap = "Spectral_r", vmin = 0, vmax = 2)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (afile_suburb["SensibleHeatFlux"]/afile_suburb["LatentHeatFlux"]).isel(y = slice(200,800)), cmap = "Spectral_r", vmin = 0, vmax = 2)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (afile_pastureconiforest["SensibleHeatFlux"]/afile_pastureconiforest["LatentHeatFlux"]).isel(y = slice(200,800)), cmap = "Spectral_r", vmin = 0, vmax = 2)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (afile_suburbconiforest["SensibleHeatFlux"]/afile_suburbconiforest["LatentHeatFlux"]).isel(y = slice(200,800)), cmap = "Spectral_r", vmin = 0, vmax = 2)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (afile_suburbpasture["SensibleHeatFlux"]/afile_suburbpasture["LatentHeatFlux"]).isel(y = slice(200,800)), cmap = "Spectral_r", vmin = 0, vmax = 2)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "white", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(bwmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "both"); cbar.set_label("Bowen Ratio")
            fig.savefig(f"{figprepath}/bowen_{t.hour}{str(t.minute).zfill(2)}z.png")
        
        elif field == "SrfPres":
            fig.suptitle(f"Surface Pressure at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
            presmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["Pressure"].isel(z=0, y = slice(200,800)), cmap = "RdBu", vmin = 1014, vmax = 1017)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["Pressure"].isel(z=0, y = slice(200,800)), cmap = "RdBu", vmin = 1014, vmax = 1017)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["Pressure"].isel(z=0, y = slice(200,800)), cmap = "RdBu", vmin = 1014, vmax = 1017)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["Pressure"].isel(z=0, y = slice(200,800)), cmap = "RdBu", vmin = 1014, vmax = 1017)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["Pressure"].isel(z=0, y = slice(200,800)), cmap = "RdBu", vmin = 1014, vmax = 1017)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["Pressure"].isel(z=0, y = slice(200,800)), cmap = "RdBu", vmin = 1014, vmax = 1017)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "white", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(presmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "both"); cbar.set_label("Surface Pressure (hPa)")
            fig.savefig(f"{figprepath}/srfpres_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "PresPert":
            fig.suptitle(f"Surface Pressure Anomaly at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
            prespertmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["Pressure"].isel(z=0, y = slice(200,800))-afile_unipasture["Pressure"].isel(z=0, y = slice(500,800)).mean(), cmap = "RdBu", vmin = -1.5, vmax = 1.5)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["Pressure"].isel(z=0, y = slice(200,800))-afile_coniforest["Pressure"].isel(z=0, y = slice(500,800)).mean(), cmap = "RdBu", vmin = -1.5, vmax = 1.5)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["Pressure"].isel(z=0, y = slice(200,800))-afile_suburb["Pressure"].isel(z=0, y = slice(500,800)).mean(), cmap = "RdBu", vmin = -1.5, vmax = 1.5)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["Pressure"].isel(z=0, y = slice(200,800))-afile_pastureconiforest["Pressure"].isel(z=0, y = slice(500,800)).mean(), cmap = "RdBu", vmin = -1.5, vmax = 1.5)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["Pressure"].isel(z=0, y = slice(200,800))-afile_suburbconiforest["Pressure"].isel(z=0, y = slice(500,800)).mean(), cmap = "RdBu", vmin = -1.5, vmax = 1.5)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["Pressure"].isel(z=0, y = slice(200,800))-afile_suburbpasture["Pressure"].isel(z=0, y = slice(500,800)).mean(), cmap = "RdBu", vmin = -1.5, vmax = 1.5)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "white", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(prespertmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "both"); cbar.set_label("Surface Pressure (hPa)")
            fig.savefig(f"{figprepath}/prespert_{t.hour}{str(t.minute).zfill(2)}z.png")
                
        elif field == "VaporMix":
            fig.suptitle(f"Near-Surface Vapor Mixing Ratio at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
            vapmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["VaporMix"].isel(z=5,y = slice(200, 800)), cmap = "BrBG", vmin = 10, vmax = 20)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["VaporMix"].isel(z=5,y = slice(200, 800)), cmap = "BrBG", vmin = 10, vmax = 20)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["VaporMix"].isel(z=5,y = slice(200, 800)), cmap = "BrBG", vmin = 10, vmax = 20)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["VaporMix"].isel(z=5,y = slice(200, 800)), cmap = "BrBG", vmin = 10, vmax = 20)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["VaporMix"].isel(z=5,y = slice(200, 800)), cmap = "BrBG", vmin = 10, vmax = 20)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["VaporMix"].isel(z=5,y = slice(200, 800)), cmap = "BrBG", vmin = 10, vmax = 20)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "white", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(vapmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "max"); cbar.set_label(r"Vapor Mixing Ratio $(g \ kg^{-1})$")
            fig.savefig(f"{figprepath}/vapmix_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "CloudTop":
            fig.suptitle(f"Cloud Top Height at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
            cldtopmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["CloudTopHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 16000)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["CloudTopHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 16000)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["CloudTopHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 16000)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["CloudTopHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 16000)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["CloudTopHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 16000)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["CloudTopHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 16000)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "white", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "white", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                ax.set_facecolor("black")
                shoreline = ax.axhline(301, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "white", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(cldtopmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "max"); cbar.set_label("Cloud Top Height (m)")
            fig.savefig(f"{figprepath}/cldtop_{t.hour}{str(t.minute).zfill(2)}z.png")

        # elif field == "CloudBase":
        #     from palettable.cartocolors.sequential import Emrld_7
        #     cldbasecmap = Emrld7.get_mpl_colormap().reversed()
        #     fig.suptitle(f"Cloud Base Height at {(t-timedelta(hours=5)).strftime('%H%M')} LT")
        #     cldbasemp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["CloudBaseHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 4000)
        #     ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["CloudBaseHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 4000)
        #     ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["CloudBaseHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 4000)
        #     ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["CloudBaseHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 4000)
        #     ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["CloudBaseHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 4000)
        #     ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["CloudBaseHeight"].isel(y = slice(200, 800)), cmap = "gist_earth", vmin = 0, vmax = 4000)
        #     for ax in (ax21, ax22, ax23):
        #         forestbounds = ax.plot([100, 100], [300, 800], color = "white", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
        #         ax.plot([300, 300], [300, 800], color = "white", linestyle = "--", linewidth = 0.5)
        #     for ax in fig.get_axes():
        #         ax.set_facecolor("black")
        #         shoreline = ax.axhline(301, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
        #         ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "white", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
        #     cbar = fig.colorbar(cldbasemp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "max"); cbar.set_label("Cloud Base Height (m)")
        #     fig.savefig(f"{figprepath}/cldbase_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "VertIntCond":
            pasturecond = afile_unipasture["VertIntCond"]
            coniforestcond = afile_coniforest["VertIntCond"]
            suburbcond = afile_suburb["VertIntCond"]
            pastureconiforestcond = afile_pastureconiforest["VertIntCond"]
            suburbconiforestcond = afile_suburbconiforest["VertIntCond"]
            suburbpasturecond = afile_suburbpasture["VertIntCond"]      
            from palettable.cmocean.sequential import Thermal_10
            condcmap = Thermal_10.get_mpl_colormap()
            condnorm = BoundaryNorm(boundaries = [0, 1, 5, 10, 20, 30, 40, 50], ncolors = 256, extend = "max")
            fig.suptitle(f"Vertically Integrated Condensate at {(t-timedelta(hours = 5)).strftime('%H%M')} LT", fontfamily = "Liberation Serif")
            condmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (pasturecond.where(pasturecond>0.5)).isel(y = slice(200,800)), cmap = condcmap, norm = condnorm)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (coniforestcond.where(coniforestcond>0.5)).isel(y = slice(200,800)), cmap = condcmap, norm = condnorm)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbcond.where(suburbcond>0.5)).isel(y = slice(200,800)), cmap = condcmap, norm = condnorm)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (pastureconiforestcond.where(pastureconiforestcond>0.5)).isel(y = slice(200,800)), cmap = condcmap, norm = condnorm)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbconiforestcond.where(suburbconiforestcond>0.5)).isel(y = slice(200,800)), cmap = condcmap, norm = condnorm)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbpasturecond.where(suburbpasturecond>0.5)).isel(y=slice(200,800)), cmap = condcmap, norm = condnorm)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "black", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "black", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(condmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "max"); cbar.set_label("Vertically Integrated Condensate (mm Liquid Equivalent)")
            fig.savefig(f"{figprepath}/vertintcond_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "VertIntIce":
            from palettable.cmocean.sequential import Ice_10
            icecmap = Ice_10.get_mpl_colormap().reversed()
            condnorm = BoundaryNorm(boundaries = [0, 1, 5, 10, 20, 30, 40, 50], ncolors = 256, extend = "max")
            pastureice = afile_unipasture["VertIntIce"]
            coniforestice = afile_coniforest["VertIntIce"]
            suburbice = afile_suburb["VertIntIce"]
            pastureconiforestice = afile_pastureconiforest["VertIntIce"]
            suburbconiforestice = afile_suburbconiforest["VertIntIce"]
            suburbpastureice = afile_suburbpasture["VertIntIce"]                         
            fig.suptitle(f"Vertically Integrated Condensate at {(t-timedelta(hours = 5)).strftime('%H%M')} LT", fontfamily = "Liberation Serif")
            icemp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (pastureice.where(pastureice>0.5)).isel(y = slice(200,800)), cmap = icecmap, norm = condnorm)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (coniforestice.where(coniforestice>0.5)).isel(y = slice(200,800)), cmap = icecmap, norm = condnorm)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbice.where(suburbice>0.5)).isel(y = slice(200,800)), cmap = icecmap, norm = condnorm)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (pastureconiforestice.where(pastureconiforestice>0.5)).isel(y = slice(200,800)), cmap = icecmap, norm = condnorm)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbconiforestice.where(suburbconiforestice>0.5)).isel(y = slice(200,800)), cmap = icecmap, norm = condnorm)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbpastureice.where(suburbpastureice>0.5)).isel(y = slice(200,800)), cmap = icecmap, norm = condnorm)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "black", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "black", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(icemp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "max"); cbar.set_label("Vertically Integrated Ice (mm Liquid Equivalent)")
            fig.savefig(f"{figprepath}/vertintice_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "VertIntLiq":
            from palettable.cmocean.sequential import Algae_10
            liqcmap = Algae_10.get_mpl_colormap()
            pastureliq = afile_unipasture["VertIntLiq"]
            coniforestliq = afile_coniforest["VertIntLiq"]
            suburbliq = afile_suburb["VertIntLiq"]
            pastureconiforestliq = afile_pastureconiforest["VertIntLiq"]
            suburbconiforestliq = afile_suburbconiforest["VertIntLiq"]
            suburbpastureliq = afile_suburbpasture["VertIntLiq"]
            condnorm = BoundaryNorm(boundaries = [0, 1, 5, 10, 20, 30, 40, 50], ncolors = 256, extend = "max")
            fig.suptitle(f"Vertically Integrated Condensate at {(t-timedelta(hours = 5)).strftime('%H%M')} LT", fontfamily = "Liberation Serif")
            liqmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (pastureliq.where(pastureliq>0.5)).isel(y = slice(200,800)), cmap = liqcmap, norm = condnorm)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (coniforestliq.where(coniforestliq>0.5)).isel(y = slice(200,800)), cmap = liqcmap, norm = condnorm)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbliq.where(suburbliq>0.5)).isel(y = slice(200,800)), cmap = liqcmap, norm = condnorm)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (pastureconiforestliq.where(pastureconiforestliq>0.5)).isel(y = slice(200,800)), cmap = liqcmap, norm = condnorm)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbconiforestliq.where(suburbconiforestliq>0.5)).isel(y = slice(200,800)), cmap = liqcmap, norm = condnorm)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), (suburbpastureliq.where(suburbpastureliq>0.5)).isel(y=slice(200,800)), cmap = liqcmap, norm = condnorm)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "black", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "black", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(liqmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "max"); cbar.set_label("Vertically Integrated Liquid (mm Liquid Equivalent)")
            fig.savefig(f"{figprepath}/vertintliq_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "UWind":
            fig.suptitle(f"Near-Surface Zonal Wind at {(t-timedelta(hours = 5)).strftime('%H%M')} LT", fontfamily = "Liberation Serif")
            uwindmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["u"].isel(z=5, y = slice(200, 800)), cmap = "bwr", vmin = -10, vmax = 10)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["u"].isel(z=5, y = slice(200, 800)), cmap = "bwr", vmin = -10, vmax = 10)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["u"].isel(z=5, y = slice(200, 800)), cmap = "bwr", vmin = -10, vmax = 10)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["u"].isel(z=5, y = slice(200, 800)), cmap = "bwr", vmin = -10, vmax = 10)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["u"].isel(z=5, y = slice(200, 800)), cmap = "bwr", vmin = -10, vmax = 10)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["u"].isel(z=5, y = slice(200, 800)), cmap = "bwr", vmin = -10, vmax = 10)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "black", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "black", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(uwindmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "both"); cbar.set_label(r"Eastward Wind Velocity $(m \ s^{-1})$", fontfamily = "Liberation Serif")
            fig.savefig(f"{figprepath}/uwind_{t.hour}{str(t.minute).zfill(2)}z.png")

        elif field == "SrfTemp":
            from palettable.colorbrewer.diverging import Spectral_10
            tempcmap = Spectral_10.get_mpl_colormap().reversed()
            fig.suptitle(f"Near-Surface Air Temperature at {(t-timedelta(hours = 5)).strftime('%H%M')} LT", fontfamily = "Liberation Serif")
            tempmp = ax11.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_unipasture["SrfTemp"].isel(y = slice(200,800)), cmap = tempcmap, vmin = 300, vmax = 312)
            ax12.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_coniforest["SrfTemp"].isel(y = slice(200, 800)), cmap = tempcmap, vmin = 300, vmax = 312)
            ax13.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburb["SrfTemp"].isel(y = slice(200, 800)), cmap = tempcmap, vmin = 300, vmax = 312)
            ax21.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_pastureconiforest["SrfTemp"].isel(y = slice(200,800)), cmap = tempcmap, vmin = 300, vmax = 312)
            ax22.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbconiforest["SrfTemp"].isel(y = slice(200, 800)), cmap = tempcmap, vmin = 300, vmax = 312)
            ax23.pcolormesh(np.linspace(0, 400, 401), np.linspace(200, 800, 601), afile_suburbpasture["SrfTemp"].isel(y = slice(200,800)), cmap = tempcmap, vmin = 300, vmax = 312)
            # for ax in fig.get_axes():
            #     ax.axhline(300, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
            #     ax.legend(loc = "lower left", fontsize = 8)
            for ax in (ax21, ax22, ax23):
                forestbounds = ax.plot([100, 100], [300, 800], color = "black", linestyle = "--", label = "Stripe Boundaries", linewidth = 0.5)
                ax.plot([300, 300], [300, 800], color = "black", linestyle = "--", linewidth = 0.5)
            for ax in fig.get_axes():
                shoreline = ax.axhline(301, color = "white", linestyle = "-.", label = "Shoreline", linewidth = 0.5)
                ax.legend(loc  = "lower left", framealpha = 0, fontsize = 6.5, labelcolor = "white", bbox_to_anchor = (0, 0), borderaxespad = 0, borderpad = 0.1)
            cbar = fig.colorbar(tempmp, ax = fig.get_axes(), orientation = "horizontal", fraction = 0.05, extend = "both"); cbar.set_label("Air Temperature (K)", fontfamily = "Liberation Serif")
            fig.savefig(f"{figprepath}/srftemp_{t.hour}{str(t.minute).zfill(2)}z.png")

        plt.close(); del fig; del ax11; del ax12; del ax13; del ax21; del ax22; del ax23; del cbar



            # ax1.set_title(f"Cross-Shore Meridional Wind at time {t.hour}{str(t.minute).zfill(2)}Z", y = 1.02)
            # vmp = ax1.pcolormesh(np.linspace(-1500, 2500, 801), gprops["wzstarlvs"][:41], convvwind-convvwind.mean(axis=1)[:,None], cmap = "bwr", vmin = -5, vmax = 5, shading = "flat")
            # fig.colorbar(vmp, ax = ax1, orientation = "horizontal", fraction = 0.05, label = "Meridional Wind (m/s)", extend = "both")
            # fig.savefig(f"{folderprepath}{case}figures/vxccross_{t.hour}{str(t.minute).zfill(2)}z.png")
            # ax1.set_title(f"Cross-Shore Water Vapor at time {t.hour}{str(t.minute).zfill(2)}Z", y = 1.02)
            # vapmp = ax1.pcolormesh(np.linspace(-1500, 2500, 801), gprops["wzstarlvs"][:41], afile["VaporMix"].isel(z = slice(0, 40), x = slice(150,250)).mean(dim = "x"), cmap = "BrBG", vmin = 3, vmax = 20, shading = "flat", zorder = 0)
            # fig.colorbar(vapmp, ax = ax1, orientation = "horizontal", fraction = 0.05, label = "Vapor Mixing Ratio (g/kg)", extend = "both")
            # fig.savefig(f"{folderprepath}{case}figures/vapxccross_{t.hour}{str(t.minute).zfill(2)}z.png")
            # ax1.set_title(f"Cross-Shore Theta Anomaly at time {t.hour}{str(t.minute).zfill(2)}Z", y = 1.02)
            # thetamp = ax1.pcolormesh(np.linspace(-1500, 2500, 801), gprops["wzstarlvs"][:41], (afile["Theta"]-afile["Theta"].mean(dim = "y")).isel(z = slice(0, 40), x = slice(150, 250)).mean(dim = "x"), cmap = "bwr", vmin = -5, vmax = 5, shading = "flat", zorder = 0)
            # fig.colorbar(vmp, ax = ax1, orientation = "horizontal", fraction = 0.05, label = "Theta Anomaly (K)", extend = "both")
            # fig.savefig(f"{folderprepath}{case}figures/thanomxccross_{t.hour}{str(t.minute).zfill(2)}z.png")
            # plt.close(); del fig; del ax1; afile.close(); del afile
        # afile_unipasture = xr.open_dataset("/moonbow/ascheb/idealized/unipasture-wind/processed_data/mergedvars_2022-06-17-190000_newroll_dasktest.nc")
    afile_unipasture.close(); del afile_unipasture
    afile_coniforest.close(); del afile_coniforest
    afile_suburb.close(); del afile_suburb
    afile_pastureconiforest.close(); del afile_pastureconiforest
    afile_suburbconiforest.close(); del afile_suburbconiforest
    afile_suburbpasture.close(); del afile_suburbpasture
    return ftime

# t = datetime(2022, 6, 17, 18, 0, 0)
# make_combplots(t)
# ppool = ProcessPoolExecutor(max_workers = 6)

# st = perf_counter()
# folderprepath = "/moonbow/ascheb/idealized/"
# t0 = datetime.strptime("2022-06-17-140000", "%Y-%m-%d-%H%M%S")
# tlist = []
# for i in range(0, 55):
#     t = t0+timedelta(minutes = 10*i)
#     tlist.append(t)
#     # make_combplots_forestsoil(t)
# print(tlist)
# ppool = ProcessPoolExecutor(max_workers = 16) 
# ppool.map(make_combplots_forestsoil, tlist)
# ppool.shutdown()
# et = perf_counter()
# print(f"Plotting took {et-st:.2f} seconds")

# folderprepath = "/moonbow/ascheb/idealized/"
# reload(mkv)
# # fields = ["bowen"]
# fields = ["srftemp", "rainrate", "srfpres", "vapplan", "cldtop", "uwind", "lhflux", "shflux", "bowen", "vertintcond", "vertintice", "vertintliq"]
# pltstrings = glob(f"{figprepath}/*.png")
# for field in fields:
#     if any [pltstring.contains(field) for pltstring in pltstrings]
#     mkv.makevidcomb(folderprepath, "paperplots", field)
runtype = input("Do you want to *plot*, *animate* existing plots, or do *both*? ")
figprepath = input("Enter the path to where the figures are stored: ")
if runtype.lower() == "plot":
    st = perf_counter()
    t0 = input("Enter the start time for plotting in yyyy-mm-dd-HHMMSS format: ")
    tf = input("Enter the end time for plotting in yyyy-mm-dd-HHMMSS format: ")
    fields = input("Enter the list of fields you want to plot, as comma-separated values: ")
    fields = fields.split(",")
    fields = [i.strip() for i in fields]
    # if "Div" in fields:
    #     fields.remove("Div")
    # plotdiv = True
    partial_combplots = partial(make_combplots, figprepath, fields)
    tlist = date_range(t0, tf, freq = timedelta(minutes = 10)).to_pydatetime()
    seq = input("Is this a test run? Yes or No? ")
    if seq.lower() == "yes":
        for t in tlist:
            make_combplots(figprepath, fields, t)
            # if plotdiv:
            #     make_divplots(t)
    elif seq.lower() == "no":
        with ProcessPoolExecutor(max_workers = 4) as ppool:
            ppool.map(partial_combplots, tlist)
            # if plotdiv:
            #     ppool.map(make_divplots, tlist)
            ppool.shutdown()
    else:
        raise Exception("Must be *yes* or *no*!")
    et = perf_counter()
    print(f"Plotting took {et-st:.2f} seconds")
    
    
elif runtype.lower() == "animate":
    st = perf_counter()
    reload(mkv)
    # fields = ["bowen"]
    #fields = ["srftemp", "rainrate", "srfpres", "vapplan", "cldtop", "uwind", "lhflux", "shflux", "bowen", "vertintcond"]
    # fields = ["snowrate", "shcomp", "lhcomp", "cldtop", "vapcomp", "divcomp", "wcomp"]
    # fields = ["w"]
    fields = input("Enter the list of fields to plot, as comma-separated variables (here, they're all lowercase)")
    fields = [f.strip().lower() for f in fields.split(",")]
    for field in fields:
        mkv.makevidcomb(figprepath, field)
    et = perf_counter()
    print(f"Animation took {et-st:.2f} seconds")
    
elif runtype.lower() == "both":
    st = perf_counter()
    t0 = input("Enter the start time for plotting in yyyy-mm-dd-HHMMSS format: ")
    tf = input("Enter the end time for plotting in yyyy-mm-dd-HHMMSS format: ")
    fields = input("Enter the list of fields you want to plot, as comma-separated values: ")
    fields = fields.split(",")
    fields = [i.strip() for i in fields]
    # if "Div" in fields:
    #     fields.remove("Div")
    # plotdiv = True
    partial_combplots = partial(make_combplots, figprepath, fields)
    tlist = date_range(t0, tf, freq = timedelta(minutes = 10)).to_pydatetime()
    seq = input("Is this a test run? Yes or No? ")
    if seq.lower() == "yes":
        for t in tlist:
            make_combplots(figprepath, fields, t)
            # if plotdiv:
            #     make_divplots(t)
    elif seq.lower() == "no":
       with ProcessPoolExecutor(max_workers = 4) as ppool:
            ppool.map(partial_combplots, tlist)
            # if plotdiv:
            #     ppool.map(make_divplots, tlist)
            ppool.shutdown()
    et = perf_counter()
    print(f"Plotting took {et-st:.2f} seconds")
    st = perf_counter()
    reload(mkv)
    # fields = ["bowen"]
    fields = ["srftemp", "rainrate", "srfpres", "vapmix", "cldtop", "uwind", "lhflux", "shflux", "bowen"]
    # fields = ["snowrate", "shcomp", "lhcomp", "cldtop", "vapcomp", "divcomp", "wcomp"]
    for field in fields:
        mkv.makevidcomb(figprepath, field)
    et = perf_counter()
    print(f"Animation took {et-st:.2f} seconds")
else:
    raise Exception("Runtype must be either plot, animate, or both!")