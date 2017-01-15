/*
 * Copyright (c) 2008, Jerome Fimes, Communications & Systemes <jerome.fimes@c-s.fr>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS `AS IS'
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#include "opj_config.h"
#include "openjpeg.h"
#include "stdlib.h"

/* -------------------------------------------------------------------------- */

/**
sample error debug callback expecting no client object
*/
static void error_callback(const char *msg, void *client_data) {
	(void)client_data;
	fprintf(stdout, "[ERROR] %s", msg);
}
/**
sample warning debug callback expecting no client object
*/
static void warning_callback(const char *msg, void *client_data) {
	(void)client_data;
	fprintf(stdout, "[WARNING] %s", msg);
}
/**
sample debug callback expecting no client object
*/
static void info_callback(const char *msg, void *client_data) {
	(void)client_data;
	fprintf(stdout, "[INFO] %s", msg);
}

/* -------------------------------------------------------------------------- */

#define NUM_COMPS_MAX 4
int main (int argc, char *argv[])
{
	opj_cparameters_t l_param;
	opj_codec_t * l_codec;
	opj_image_t * l_image;
	opj_image_cmptparm_t l_params [NUM_COMPS_MAX];
	FILE * l_file;
	opj_stream_t * l_stream;
	OPJ_UINT32 l_nb_tiles;
	OPJ_UINT32 l_data_size;
	unsigned char len;

#ifdef USING_MCT
	const OPJ_FLOAT32 l_mct [] =
	{
		1 , 0 , 0 ,
		0 , 1 , 0 ,
		0 , 0 , 1
	};

	const OPJ_INT32 l_offsets [] =
	{
		128 , 128 , 128
	};
#endif

	opj_image_cmptparm_t * l_current_param_ptr;
	OPJ_UINT32 i;
	OPJ_BYTE *l_data;

  OPJ_UINT32 num_comps;
  int image_width;
  int image_height;
  int tile_width;
  int tile_height;
  int comp_prec;
  int irreversible;
  char output_file[64];

  /* should be test_tile_encoder 3 2000 2000 1000 1000 8 tte1.j2k */
  if( argc == 9 )
    {
    num_comps = (OPJ_UINT32)atoi( argv[1] );
    image_width = atoi( argv[2] );
    image_height = atoi( argv[3] );
    tile_width = atoi( argv[4] );
    tile_height = atoi( argv[5] );
    comp_prec = atoi( argv[6] );
    irreversible = atoi( argv[7] );
    strcpy(output_file, argv[8] );
    }
  else
    {
    num_comps = 3;
    image_width = 2000;
    image_height = 2000;
    tile_width = 1000;
    tile_height = 1000;
    comp_prec = 8;
    irreversible = 1;
    strcpy(output_file, "test.j2k" );
    }
  if( num_comps > NUM_COMPS_MAX )
    {
    return 1;
    }
	l_nb_tiles = (OPJ_UINT32)(image_width/tile_width) * (OPJ_UINT32)(image_height/tile_height);
	l_data_size = (OPJ_UINT32)tile_width * (OPJ_UINT32)tile_height * (OPJ_UINT32)num_comps * (OPJ_UINT32)(comp_prec/8);

	l_data = (OPJ_BYTE*) malloc(l_data_size * sizeof(OPJ_BYTE));

	fprintf(stdout, "Encoding random values -> keep in mind that this is very hard to compress\n");
	for (i=0;i<l_data_size;++i)	{
		l_data[i] = (OPJ_BYTE)i; /*rand();*/
	}

	opj_set_default_encoder_parameters(&l_param);
	/** you may here add custom encoding parameters */
	/* rate specifications */
	/** number of quality layers in the stream */
	l_param.tcp_numlayers = 1;
	l_param.cp_fixed_quality = 1;
	l_param.tcp_distoratio[0] = 20;
	/* is using others way of calculation */
	/* l_param.cp_disto_alloc = 1 or l_param.cp_fixed_alloc = 1 */
	/* l_param.tcp_rates[0] = ... */


	/* tile definitions parameters */
	/* position of the tile grid aligned with the image */
	l_param.cp_tx0 = 0;
	l_param.cp_ty0 = 0;
	/* tile size, we are using tile based encoding */
	l_param.tile_size_on = OPJ_TRUE;
	l_param.cp_tdx = tile_width;
	l_param.cp_tdy = tile_height;

	/* use irreversible encoding ?*/
	l_param.irreversible = irreversible;

	/* do not bother with mct, the rsiz is set when calling opj_set_MCT*/
	/*l_param.cp_rsiz = OPJ_STD_RSIZ;*/

	/* no cinema */
	/*l_param.cp_cinema = 0;*/

	/* no not bother using SOP or EPH markers, do not use custom size precinct */
	/* number of precincts to specify */
	/* l_param.csty = 0;*/
	/* l_param.res_spec = ... */
	/* l_param.prch_init[i] = .. */
	/* l_param.prcw_init[i] = .. */


	/* do not use progression order changes */
	/*l_param.numpocs = 0;*/
	/* l_param.POC[i].... */

	/* do not restrain the size for a component.*/
	/* l_param.max_comp_size = 0; */

	/** block encoding style for each component, do not use at the moment */
	/** J2K_CCP_CBLKSTY_TERMALL, J2K_CCP_CBLKSTY_LAZY, J2K_CCP_CBLKSTY_VSC, J2K_CCP_CBLKSTY_SEGSYM, J2K_CCP_CBLKSTY_RESET */
	/* l_param.mode = 0;*/

	/** number of resolutions */
	l_param.numresolution = 6;

	/** progression order to use*/
	/** OPJ_LRCP, OPJ_RLCP, OPJ_RPCL, PCRL, CPRL */
	l_param.prog_order = OPJ_LRCP;

	/** no "region" of interest, more precisally component */
	/* l_param.roi_compno = -1; */
	/* l_param.roi_shift = 0; */

	/* we are not using multiple tile parts for a tile. */
	/* l_param.tp_on = 0; */
	/* l_param.tp_flag = 0; */

	/* if we are using mct */
#ifdef USING_MCT
	opj_set_MCT(&l_param,l_mct,l_offsets,NUM_COMPS);
#endif


	/* image definition */
	l_current_param_ptr = l_params;
	for (i=0;i<num_comps;++i) {
		/* do not bother bpp useless */
		/*l_current_param_ptr->bpp = COMP_PREC;*/
		l_current_param_ptr->dx = 1;
		l_current_param_ptr->dy = 1;

		l_current_param_ptr->h = (OPJ_UINT32)image_height;
		l_current_param_ptr->w = (OPJ_UINT32)image_width;

		l_current_param_ptr->sgnd = 0;
		l_current_param_ptr->prec = (OPJ_UINT32)comp_prec;

		l_current_param_ptr->x0 = 0;
		l_current_param_ptr->y0 = 0;

		++l_current_param_ptr;
	}

  /* should we do j2k or jp2 ?*/
  len = (unsigned char)strlen( output_file );
  if( strcmp( output_file + len - 4, ".jp2" ) == 0 )
    {
    l_codec = opj_create_compress(OPJ_CODEC_JP2);
    }
  else
    {
    l_codec = opj_create_compress(OPJ_CODEC_J2K);
    }
	if (!l_codec) {
		return 1;
	}

	/* catch events using our callbacks and give a local context */
	opj_set_info_handler(l_codec, info_callback,00);
	opj_set_warning_handler(l_codec, warning_callback,00);
	opj_set_error_handler(l_codec, error_callback,00);

	l_image = opj_image_tile_create(num_comps,l_params,OPJ_CLRSPC_SRGB);
	if (! l_image) {
		opj_destroy_codec(l_codec);
		return 1;
	}

	l_image->x0 = 0;
	l_image->y0 = 0;
	l_image->x1 = (OPJ_UINT32)image_width;
	l_image->y1 = (OPJ_UINT32)image_height;
	l_image->color_space = OPJ_CLRSPC_SRGB;

	if (! opj_setup_encoder(l_codec,&l_param,l_image)) {
		fprintf(stderr, "ERROR -> test_tile_encoder: failed to setup the codec!\n");
		opj_destroy_codec(l_codec);
		opj_image_destroy(l_image);
		return 1;
	}

	l_file = fopen(output_file,"wb");
	if (! l_file) {
		fprintf(stderr, "ERROR -> test_tile_encoder: failed to create the output file!\n");
		opj_destroy_codec(l_codec);
		opj_image_destroy(l_image);
		return 1;
	}

	l_stream = opj_stream_create_default_file_stream(l_file, OPJ_FALSE);
    if (! l_stream) {
		fprintf(stderr, "ERROR -> test_tile_encoder: failed to create the stream from the output file %s !\n",output_file );
		fclose(l_file);
		opj_destroy_codec(l_codec);
		opj_image_destroy(l_image);
		return 1;
	}

	if (! opj_start_compress(l_codec,l_image,l_stream)) {
		fprintf(stderr, "ERROR -> test_tile_encoder: failed to start compress!\n");
		opj_stream_destroy(l_stream);
		fclose(l_file);
		opj_destroy_codec(l_codec);
		opj_image_destroy(l_image);
		return 1;
	}

	for (i=0;i<l_nb_tiles;++i) {
		if (! opj_write_tile(l_codec,i,l_data,l_data_size,l_stream)) {
			fprintf(stderr, "ERROR -> test_tile_encoder: failed to write the tile %d!\n",i);
			opj_stream_destroy(l_stream);
			fclose(l_file);
			opj_destroy_codec(l_codec);
			opj_image_destroy(l_image);
			return 1;
		}
	}

	if (! opj_end_compress(l_codec,l_stream)) {
		fprintf(stderr, "ERROR -> test_tile_encoder: failed to end compress!\n");
		opj_stream_destroy(l_stream);
		fclose(l_file);
		opj_destroy_codec(l_codec);
		opj_image_destroy(l_image);
		return 1;
	}

	opj_stream_destroy(l_stream);
	fclose(l_file);
	opj_destroy_codec(l_codec);
	opj_image_destroy(l_image);

	free(l_data);

	/* Print profiling*/
	/*PROFPRINT();*/

	return 0;
}






