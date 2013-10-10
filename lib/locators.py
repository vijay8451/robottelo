#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

locators = {

    # Login
    "login.username": "username",
    "login.password": "password",
    "login.submit": "commit",
    "login.gravatar": "//span[@class='gravatar-span']",
    "login.user": "span.ng-binding",
    "login.error": "div.jnotify-message",
    "login.interstitial": "interstitial",
    "login.logout": "logout",

    # Menus

    ## Administer
    "menu.administer": "//nav[@class='nav admin_menu right']/ul/li/a/span[@class='ng-binding']",
    "submenu.organizations": "//ul[@class='dropdown dropdown-right dropdown-active']/li[1]/a",
    "submenu.users": "//ul[@class='dropdown dropdown-right dropdown-active']/li[2]/a",
    "submenu.roles": "//ul[@class='dropdown dropdown-right dropdown-active']/li[3]/a",
    "submenu.about": "//ul[@class='dropdown dropdown-right dropdown-active']/li[4]/a"

}
