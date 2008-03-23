/*
 * Copyright (c) 2008   Rodney (moonbeam) Cryderman <rcryderman@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Library General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor Boston, MA 02110-1301,  USA
 */
 
 
#include <libawn/awn-config-client.h>

#include "applet.h"
#include "configuration.h"

static char * get_string(WebApplet * webapplet,const gchar * key)
{
  char * str;
  str=awn_config_client_get_string(webapplet->instance_config,
                                                AWN_CONFIG_CLIENT_DEFAULT_GROUP,
                                                key, NULL);
  if (!str)
  {
    str=awn_config_client_get_string(webapplet->default_config,
                                                AWN_CONFIG_CLIENT_DEFAULT_GROUP,
                                                key, NULL);
  }
  return str;
}                    

void init_config(WebApplet * webapplet, gchar * uid)
{
	webapplet->default_config = awn_config_client_new_for_applet (APPLET_NAME, NULL);
  webapplet->instance_config = awn_config_client_new_for_applet (APPLET_NAME, uid);

  webapplet->uri=get_string(webapplet,CONFIG_URI);
}

