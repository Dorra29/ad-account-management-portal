import logging

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@login_required
def dashboard_redirect(request):

    ad_groups = request.session.get("ad_groups", [])

    logger.debug("Dashboard redirect, AD groups: %s", ad_groups)

    for group in ad_groups:

        if "GG_Admins" in group:
            return redirect("/admin-dashboard/")

        if "GG_SupportAdmins" in group:
            return redirect("/admin-dashboard/")

        if "GG_Managers" in group:
            return redirect("/manager-dashboard/")

        if "GG_Employees" in group:
            return redirect("/employee-dashboard/")

    return redirect("/no-access/")
